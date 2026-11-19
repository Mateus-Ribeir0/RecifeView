from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.acessos_corporativos.acessos import (
    CriarAcessoCorporativo,
    DadosDoAcesso,
    NovoAcesso,
)
from app.application.casos_de_uso.acessos_corporativos.convite import AceitarConvite
from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
)
from app.application.casos_de_uso.encaminhamentos.avisos import AvisosDoCiclo
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.retorno import (
    RegistrarRetornoPelaGestao,
    RespostaAoEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso_corporativo import SituacaoDoAcesso
from app.domain.demanda_do_orgao import PeriodoEmAnos
from app.domain.email import Email
from app.domain.encaminhamento.encaminhamento import SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import NotificacaoNaoEncontrada
from app.domain.notificacao import NovaNotificacao
from app.domain.usuario import Perfil
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.acessos_corporativos import (
    AcessosCorporativosSql,
    ConviteRepositorySql,
)
from app.infrastructure.repositories.avisos import DestinatariosDosAvisosSql
from app.infrastructure.repositories.demanda_do_orgao import DemandaDoOrgaoSql
from app.infrastructure.repositories.encaminhamentos import EncaminhamentoRepositorySql
from app.infrastructure.repositories.indicadores_do_ciclo import IndicadoresDoCicloSql
from app.infrastructure.repositories.notificacoes import NotificacaoRepositorySql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import CaixaDeEmailsEmMemoria, HashDeSenhaDeTeste, RelogioFixo, criar_usuario
from tests.fakes_corporativo import ENDERECO_DO_SITE, PADRAO_DO_CONVITE
from tests.fakes_encaminhamento import DespachoEmMemoria, EntregaEmMemoria
from tests.integracao.test_importacao_e_painel import URL_DO_BANCO_DE_TESTE, preparar_esquema

pytestmark = pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)

MOMENTO = datetime(2026, 10, 26, 12, 0, tzinfo=UTC)
LOCAL = "local-de-teste"
ABERTURAS_NO_LOCAL = {1: date(2026, 9, 1), 2: date(2026, 9, 5), 3: date(2026, 11, 10)}
SENHA_FORTE = "Compesa@Recife2026"


@pytest.fixture
def fabrica(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    assert URL_DO_BANCO_DE_TESTE
    preparar_esquema(URL_DO_BANCO_DE_TESTE, monkeypatch)
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    yield sessionmaker(motor, expire_on_commit=False)
    motor.dispose()


def _inserir_importacao(sessao: Session) -> int:
    return int(
        sessao.execute(
            text(
                "INSERT INTO app.importacao (nome_do_arquivo, tamanho_em_bytes, hash_do_arquivo, "
                "status, criada_em) VALUES ('t.csv', 1, 'x', 'CONCLUIDA', now()) RETURNING id"
            )
        ).scalar_one()
    )


def _inserir_registro(sessao: Session, chave: int, valores: dict[str, object]) -> None:
    parametros = {
        "chave": chave,
        "importacao": _inserir_importacao(sessao),
        "fonte": "156_EMLURB",
        "orgao": "EMLURB",
        "bairro": "AFOGADOS",
        "id_local": LOCAL,
        **valores,
    }
    sessao.execute(
        text(
            "INSERT INTO ouro.fato_demanda (chave_registro, assinatura, importacao_id, fonte, "
            "ano, data_abertura, categoria, servico_codigo, orgao, bairro_oficial, rpa, id_local, "
            "numero_informado) VALUES (:chave, :chave, :importacao, :fonte, "
            "extract(year FROM CAST(:abertura AS date))::int, :abertura, 'DRENAGEM', 'S1', :orgao, "
            ":bairro, '5', :id_local, true)"
        ),
        parametros,
    )


def _inserir_registros_no_mesmo_local(sessao: Session) -> None:
    for chave, abertura in ABERTURAS_NO_LOCAL.items():
        _inserir_registro(sessao, chave, {"abertura": abertura})
    sessao.execute(text("REFRESH MATERIALIZED VIEW ouro.mv_camara_indicacoes"))


def _servicos(sessao: Session, relogio: RelogioFixo) -> ServicosDeEncaminhamento:
    avisos = AvisosDoCiclo(
        DestinatariosDosAvisosSql(sessao),
        EntregaEmMemoria(),
        NotificacaoRepositorySql(sessao),
        ENDERECO_DO_SITE,
    )
    repositorio = EncaminhamentoRepositorySql(sessao)
    return ServicosDeEncaminhamento(repositorio, DespachoEmMemoria(), relogio, avisos)


def _servicos_de_acessos(
    sessao: Session, emails: CaixaDeEmailsEmMemoria
) -> ServicosDeAcessosCorporativos:
    relogio = RelogioFixo(MOMENTO)
    emissor = EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15))
    return ServicosDeAcessosCorporativos(
        usuarios=UsuarioRepositorySql(sessao),
        convites=ConviteRepositorySql(sessao),
        acessos=AcessosCorporativosSql(sessao),
        senhas=HashDeSenhaDeTeste(),
        emails=emails,
        registro=RegistroDeAcessosSql(sessao),
        sessoes=GestaoDeSessoes(SessaoRepositorySql(sessao), emissor, relogio),
        relogio=relogio,
        endereco_do_site=ENDERECO_DO_SITE,
    )


def test_acesso_so_recebe_avisos_depois_do_convite_aceito(fabrica: sessionmaker[Session]) -> None:
    emails = CaixaDeEmailsEmMemoria()
    administradora = criar_usuario(
        email=Email("administracao@recife.pe.gov.br"), perfil=Perfil.ADMINISTRADOR
    )
    novo = NovoAcesso("ana@compesa.exemplo", DadosDoAcesso("Ana Souza", Orgao.COMPESA))
    with fabrica.begin() as sessao:
        UsuarioRepositorySql(sessao).adicionar(administradora)
        CriarAcessoCorporativo(_servicos_de_acessos(sessao, emails)).executar(novo, administradora)
    with fabrica() as sessao:
        (pendente,) = AcessosCorporativosSql(sessao).listar()
        antes = DestinatariosDosAvisosSql(sessao).pessoas_do_orgao(Orgao.COMPESA)
    achado = PADRAO_DO_CONVITE.search(emails.mensagens[-1].corpo)
    assert achado is not None
    with fabrica.begin() as sessao:
        AceitarConvite(_servicos_de_acessos(sessao, emails)).executar(achado.group(1), SENHA_FORTE)
    with fabrica() as sessao:
        (ativo,) = AcessosCorporativosSql(sessao).listar()
        depois = DestinatariosDosAvisosSql(sessao).pessoas_do_orgao(Orgao.COMPESA)

    assert pendente.situacao(MOMENTO) is SituacaoDoAcesso.CONVITE_ENVIADO
    assert antes == []
    assert ativo.situacao(MOMENTO) is SituacaoDoAcesso.ATIVO
    assert ativo.ultimo_acesso_em is not None
    assert [item.email for item in depois] == ["ana@compesa.exemplo"]


def test_notificacao_fica_com_a_propria_conta(fabrica: sessionmaker[Session]) -> None:
    dona, outra = criar_usuario(), criar_usuario(email=Email("outra@recife.pe.gov.br"))
    with fabrica.begin() as sessao:
        UsuarioRepositorySql(sessao).adicionar(dona)
        UsuarioRepositorySql(sessao).adicionar(outra)
        repositorio = NotificacaoRepositorySql(sessao)
        for titulo in ("Primeira", "Segunda"):
            repositorio.criar(NovaNotificacao(dona.id, titulo, "Texto", "/painel"))
    with fabrica.begin() as sessao:
        repositorio = NotificacaoRepositorySql(sessao)
        caixa = repositorio.caixa_do_usuario(dona.id, 10)
        with pytest.raises(NotificacaoNaoEncontrada):
            repositorio.marcar_lida(outra.id, caixa.itens[0].id, MOMENTO)
        repositorio.marcar_lida(dona.id, caixa.itens[0].id, MOMENTO)
        depois_de_uma = repositorio.caixa_do_usuario(dona.id, 10)
        repositorio.marcar_todas_lidas(dona.id, MOMENTO)
        depois_de_todas = repositorio.caixa_do_usuario(dona.id, 10)

    assert (caixa.nao_lidas, caixa.itens[0].titulo) == (2, "Segunda")
    assert depois_de_uma.nao_lidas == 1
    assert depois_de_todas.nao_lidas == 0


def test_encaminhamento_guarda_o_local_e_acha_o_mesmo_problema(
    fabrica: sessionmaker[Session],
) -> None:
    relogio = RelogioFixo(MOMENTO)
    with fabrica.begin() as sessao:
        _inserir_registros_no_mesmo_local(sessao)
        encaminhar = EncaminharOcorrencia(_servicos(sessao, relogio))
        primeiro = encaminhar.executar(PedidoDeEncaminhamento(1, Orgao.EMLURB))
        encaminhar.executar(PedidoDeEncaminhamento(2, Orgao.EMLURB))
    with fabrica() as sessao:
        repositorio = EncaminhamentoRepositorySql(sessao)
        guardado = repositorio.buscar(primeiro.id)
        assert guardado is not None
        comparaveis = repositorio.comparaveis([guardado.ocorrencia])
        no_local = repositorio.registros_do_mesmo_local(guardado.ocorrencia)

    assert guardado.ocorrencia.id_local == LOCAL
    assert guardado.ocorrencia.numero_informado
    assert sorted(item.ocorrencia.chave_registro for item in comparaveis) == [1, 2]
    assert no_local == 1


def test_indicadores_contam_o_ciclo_e_o_que_voltou_a_ser_pedido(
    fabrica: sessionmaker[Session],
) -> None:
    relogio = RelogioFixo(MOMENTO)
    resolvido = RespostaAoEncaminhamento(
        SituacaoDoEncaminhamento.RESOLVIDO, resposta_ao_cidadao="Galeria limpa"
    )
    with fabrica.begin() as sessao:
        _inserir_registros_no_mesmo_local(sessao)
        servicos = _servicos(sessao, relogio)
        encaminhamento = EncaminharOcorrencia(servicos).executar(
            PedidoDeEncaminhamento(1, Orgao.COMPESA)
        )
        gestora = criar_usuario()
        UsuarioRepositorySql(sessao).adicionar(gestora)
        RegistrarRetornoPelaGestao(servicos).executar(encaminhamento.id, resolvido, gestora.id)
    with fabrica() as sessao:
        indicadores = IndicadoresDoCicloSql(sessao)
        (compesa,) = indicadores.por_orgao(MOMENTO.date(), Orgao.COMPESA)
        semanas = indicadores.semanas(MOMENTO.date(), Orgao.COMPESA)
        por_tema = indicadores.resolvidas_por_tema(Orgao.COMPESA)
        opcoes = indicadores.opcoes_de_filtro(Orgao.COMPESA)
        abertas = indicadores.abertas_por_bairro(Orgao.COMPESA)

    assert (compesa.encaminhados, compesa.resolvidas, compesa.resolvidas_no_prazo) == (1, 1, 1)
    assert compesa.voltaram_a_ser_pedidas == 1
    assert compesa.mediana_de_dias_ate_resolver == 0
    assert len(semanas) == 12
    assert sum(semana.resolvidas for semana in semanas) == 1
    assert [(item.categoria, item.quantidade) for item in por_tema] == [("DRENAGEM", 1)]
    assert opcoes.bairros == ["AFOGADOS"]
    assert abertas == {}


def test_dados_do_orgao_saem_da_view_por_orgao(fabrica: sessionmaker[Session]) -> None:
    with fabrica.begin() as sessao:
        for chave, bairro in ((10, "AFOGADOS"), (11, "AFOGADOS"), (12, None)):
            _inserir_registro(
                sessao,
                chave,
                {
                    "abertura": date(2025, 5, 1),
                    "fonte": "CAMARA_REQUERIMENTOS",
                    "orgao": "COMPESA",
                    "bairro": bairro,
                    "id_local": None,
                },
            )
        sessao.execute(text("REFRESH MATERIALIZED VIEW ouro.mv_demanda_por_orgao"))
    with fabrica() as sessao:
        demanda = DemandaDoOrgaoSql(sessao).resumir(["COMPESA"], PeriodoEmAnos(2021, 2026))
        fora_do_periodo = DemandaDoOrgaoSql(sessao).resumir(["COMPESA"], PeriodoEmAnos(2012, 2020))

    assert (demanda.total, demanda.sem_bairro) == (3, 1)
    assert demanda.por_bairro == {"AFOGADOS": 2}
    assert [(item.ano, item.fonte) for item in demanda.por_ano] == [(2025, "CAMARA_REQUERIMENTOS")]
    assert fora_do_periodo.total == 0
