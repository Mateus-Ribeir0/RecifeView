from collections.abc import Iterator
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.encaminhamentos.avisos import AvisosDoCiclo
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
    PrepararEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.retorno import (
    AbrirPeloLink,
    RegistrarRetornoPeloLink,
    RespostaAoEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.encaminhamentos import FiltroDeEncaminhamentos
from app.domain.encaminhamento.encaminhamento import (
    VALIDADE_DO_LINK_DE_RETORNO,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.encaminhamento.sugestao import MotivoDaSugestao
from app.domain.erros import LinkDeRetornoInvalido
from app.infrastructure.repositories.avisos import DestinatariosDosAvisosSql
from app.infrastructure.repositories.encaminhamentos import EncaminhamentoRepositorySql
from tests.fakes import RelogioFixo
from tests.fakes_encaminhamento import ENDERECO_DO_SITE, DespachoEmMemoria, EntregaEmMemoria
from tests.integracao.test_importacao_e_painel import URL_DO_BANCO_DE_TESTE, preparar_esquema

pytestmark = pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)

CHAVE_DO_156 = 156
INDICACOES_DE_DRENAGEM = (("EMLURB", 40), ("COMPESA", 3), (None, 7))


def _inserir_base(sessao: Session) -> None:
    importacao_id = sessao.execute(
        text(
            "INSERT INTO app.importacao (nome_do_arquivo, tamanho_em_bytes, hash_do_arquivo, "
            "status, criada_em) VALUES ('teste.csv', 1, 'x', 'CONCLUIDA', now()) RETURNING id"
        )
    ).scalar_one()
    linhas: list[tuple[int, str, str, str | None, str | None]] = [
        (CHAVE_DO_156, "156_EMLURB", "SOLICITACAO DE SERVICO", "EMLURB", "2026/1")
    ]
    chave = 1000
    for orgao, quantidade in INDICACOES_DE_DRENAGEM:
        for _ in range(quantidade):
            chave += 1
            linhas.append((chave, "CAMARA_REQUERIMENTOS", "INDICACAO", orgao, None))
    for chave_registro, fonte, tipo, orgao, protocolo in linhas:
        sessao.execute(
            text(
                "INSERT INTO ouro.fato_demanda (chave_registro, assinatura, importacao_id, fonte, "
                "ano, data_abertura, categoria, tipo_registro, orgao, bairro_oficial, rpa, "
                "protocolo) VALUES (:chave, :chave, :importacao, :fonte, 2026, DATE '2026-09-01', "
                "'DRENAGEM', :tipo, :orgao, 'AFOGADOS', '5', :protocolo)"
            ),
            {
                "chave": chave_registro,
                "importacao": importacao_id,
                "fonte": fonte,
                "tipo": tipo,
                "orgao": orgao,
                "protocolo": protocolo,
            },
        )
    sessao.execute(text("REFRESH MATERIALIZED VIEW ouro.mv_camara_indicacoes"))


def _inserir_gestora(sessao: Session) -> UUID:
    gestora = uuid4()
    sessao.execute(
        text(
            "INSERT INTO app.usuario (id, email, nome, perfil, hash_da_senha, ativo, "
            "deve_trocar_senha, tentativas_falhas) VALUES "
            "(:id, :email, 'Gestora', 'GESTOR', 'x', true, false, 0)"
        ),
        {"id": gestora, "email": f"{gestora.hex}@recife.pe.gov.br"},
    )
    return gestora


@pytest.fixture
def fabrica(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    assert URL_DO_BANCO_DE_TESTE
    preparar_esquema(URL_DO_BANCO_DE_TESTE, monkeypatch)
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    fabrica = sessionmaker(motor, expire_on_commit=False)
    with fabrica.begin() as sessao:
        _inserir_base(sessao)
    yield fabrica
    motor.dispose()


def servicos_de(
    sessao: Session, despacho: DespachoEmMemoria, relogio: RelogioFixo
) -> ServicosDeEncaminhamento:
    avisos = AvisosDoCiclo(DestinatariosDosAvisosSql(sessao), EntregaEmMemoria(), ENDERECO_DO_SITE)
    return ServicosDeEncaminhamento(EncaminhamentoRepositorySql(sessao), despacho, relogio, avisos)


def test_sugestao_usa_as_indicacoes_do_tema_e_o_orgao_do_registro(
    fabrica: sessionmaker[Session],
) -> None:
    with fabrica() as sessao:
        servicos = servicos_de(sessao, DespachoEmMemoria(), RelogioFixo())
        preparo = PrepararEncaminhamento(servicos).executar(CHAVE_DO_156)

    assert preparo.ocorrencia.protocolo == "2026/1"
    assert preparo.sugestao.orgao is Orgao.EMLURB
    assert preparo.sugestao.motivo is MotivoDaSugestao.APONTADO_NO_REGISTRO
    assert preparo.sugestao.indicacoes_do_tema == 50
    compesa = next(item for item in preparo.sugestao.participacoes if item.orgao is Orgao.COMPESA)
    assert compesa.pct == pytest.approx(6.0)


def test_ciclo_completo_fica_gravado_com_eventos_e_resumo(
    fabrica: sessionmaker[Session],
) -> None:
    despacho, relogio = DespachoEmMemoria(), RelogioFixo()
    with fabrica.begin() as sessao:
        gestora = _inserir_gestora(sessao)
        pedido = PedidoDeEncaminhamento(CHAVE_DO_156, Orgao.COMPESA, gestora, "Vazamento", 7.5)
        EncaminharOcorrencia(servicos_de(sessao, despacho, relogio)).executar(pedido)
    with fabrica.begin() as sessao:
        resposta = RespostaAoEncaminhamento(SituacaoDoEncaminhamento.RESOLVIDO, "CMP-9")
        servicos = servicos_de(sessao, despacho, relogio)
        resolvido = RegistrarRetornoPeloLink(servicos).executar(despacho.ultimo_token(), resposta)

    hoje = relogio.agora().date()
    with fabrica() as sessao:
        repositorio = EncaminhamentoRepositorySql(sessao)
        resumo = repositorio.resumir(hoje)
        pagina = repositorio.listar(FiltroDeEncaminhamentos(orgao=Orgao.COMPESA), hoje)
        ultimos = repositorio.ultimos_por_chave([CHAVE_DO_156])

    assert resolvido.protocolo_do_orgao == "CMP-9"
    assert [evento.situacao.value for evento in resolvido.eventos] == ["enviado", "resolvido"]
    assert resumo.total == 1
    assert resumo.por_situacao[SituacaoDoEncaminhamento.RESOLVIDO] == 1
    assert resumo.mediana_de_dias_ate_resolver == 0
    assert pagina.total == 1
    assert ultimos[CHAVE_DO_156].orgao_sugerido is Orgao.EMLURB


def test_link_vencido_nao_e_encontrado(fabrica: sessionmaker[Session]) -> None:
    despacho, relogio = DespachoEmMemoria(), RelogioFixo()
    with fabrica.begin() as sessao:
        pedido = PedidoDeEncaminhamento(CHAVE_DO_156, Orgao.EMLURB)
        EncaminharOcorrencia(servicos_de(sessao, despacho, relogio)).executar(pedido)
    relogio.avancar(VALIDADE_DO_LINK_DE_RETORNO + timedelta(seconds=1))

    with fabrica() as sessao, pytest.raises(LinkDeRetornoInvalido):
        AbrirPeloLink(servicos_de(sessao, despacho, relogio)).executar(despacho.ultimo_token())
