from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.encaminhamentos.avisos import AvisosDoCiclo
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.lembrete import LembrarOrgaos
from app.application.casos_de_uso.encaminhamentos.retorno import (
    RegistrarRetornoPeloLink,
    RespostaAoEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.domain.encaminhamento.encaminhamento import (
    DIAS_PARA_O_ORGAO_RESPONDER,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.infrastructure.repositories.avisos import DestinatariosDosAvisosSql
from app.infrastructure.repositories.encaminhamentos import EncaminhamentoRepositorySql
from tests.fakes import RelogioFixo
from tests.fakes_encaminhamento import ENDERECO_DO_SITE, DespachoEmMemoria, EntregaEmMemoria
from tests.integracao.test_importacao_e_painel import URL_DO_BANCO_DE_TESTE, preparar_esquema

pytestmark = pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)

CHAVE = 4242
PROTOCOLO = "TESTE-4242"
GESTORA = "gestora@exemplo.gov.br"
QUEM_ACOMPANHA = "acompanha@exemplo.com"
QUEM_DESLIGOU = "desligou@exemplo.com"


def _inserir_usuario(sessao: Session, email: str, perfil: str, recebe_avisos: bool) -> UUID:
    usuario = uuid4()
    sessao.execute(
        text(
            "INSERT INTO app.usuario (id, email, nome, perfil, hash_da_senha, ativo, "
            "deve_trocar_senha, tentativas_falhas, recebe_avisos) VALUES "
            "(:id, :email, 'Pessoa', :perfil, 'x', true, false, 0, :avisos)"
        ),
        {"id": usuario, "email": email, "perfil": perfil, "avisos": recebe_avisos},
    )
    return usuario


def _acompanhar(sessao: Session, usuario: UUID) -> None:
    sessao.execute(
        text(
            "INSERT INTO app.pedido_acompanhado (usuario_id, protocolo, criado_em) "
            "VALUES (:usuario, :protocolo, now())"
        ),
        {"usuario": usuario, "protocolo": PROTOCOLO},
    )


def _inserir_base(sessao: Session) -> UUID:
    importacao = sessao.execute(
        text(
            "INSERT INTO app.importacao (nome_do_arquivo, tamanho_em_bytes, hash_do_arquivo, "
            "status, criada_em) VALUES ('t.csv', 1, 'x', 'CONCLUIDA', now()) RETURNING id"
        )
    ).scalar_one()
    sessao.execute(
        text(
            "INSERT INTO ouro.fato_demanda (chave_registro, assinatura, importacao_id, fonte, "
            "categoria, orgao, protocolo) VALUES "
            "(:chave, :chave, :importacao, 'OUVIDORIA', 'DRENAGEM', 'EMLURB', :protocolo)"
        ),
        {"chave": CHAVE, "importacao": importacao, "protocolo": PROTOCOLO},
    )
    sessao.execute(text("REFRESH MATERIALIZED VIEW ouro.mv_camara_indicacoes"))
    gestora = _inserir_usuario(sessao, GESTORA, "GESTOR", recebe_avisos=True)
    _acompanhar(sessao, _inserir_usuario(sessao, QUEM_ACOMPANHA, "CIDADAO", recebe_avisos=True))
    _acompanhar(sessao, _inserir_usuario(sessao, QUEM_DESLIGOU, "CIDADAO", recebe_avisos=False))
    return gestora


@pytest.fixture
def fabrica(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    assert URL_DO_BANCO_DE_TESTE
    preparar_esquema(URL_DO_BANCO_DE_TESTE, monkeypatch)
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    yield sessionmaker(motor, expire_on_commit=False)
    motor.dispose()


class Partes:
    def __init__(self) -> None:
        self.despacho = DespachoEmMemoria()
        self.entrega = EntregaEmMemoria()
        self.relogio = RelogioFixo(datetime.now(UTC))

    def servicos(self, sessao: Session) -> ServicosDeEncaminhamento:
        avisos = AvisosDoCiclo(DestinatariosDosAvisosSql(sessao), self.entrega, ENDERECO_DO_SITE)
        repositorio = EncaminhamentoRepositorySql(sessao)
        return ServicosDeEncaminhamento(repositorio, self.despacho, self.relogio, avisos)


def test_ciclo_avisa_so_quem_pode_receber(fabrica: sessionmaker[Session]) -> None:
    partes = Partes()
    with fabrica.begin() as sessao:
        gestora = _inserir_base(sessao)
        pedido = PedidoDeEncaminhamento(CHAVE, Orgao.EMLURB, gestora)
        EncaminharOcorrencia(partes.servicos(sessao)).executar(pedido)
    with fabrica.begin() as sessao:
        resposta = RespostaAoEncaminhamento(SituacaoDoEncaminhamento.DEVOLVIDO)
        token = partes.despacho.ultimo_token()
        RegistrarRetornoPeloLink(partes.servicos(sessao)).executar(token, resposta)

    assert len(partes.entrega.para(QUEM_ACOMPANHA)) == 2
    assert partes.entrega.para(QUEM_DESLIGOU) == []
    (aviso_da_gestao,) = partes.entrega.para(GESTORA)
    assert "Emlurb devolveu" in aviso_da_gestao.corpo
    with fabrica() as sessao:
        pendencias = EncaminhamentoRepositorySql(sessao).contar_pendencias(
            partes.relogio.agora().date()
        )
    assert (pendencias.devolvidos, pendencias.pedem_acao) == (1, 1)


def test_lembrete_fica_registrado_e_nao_se_repete(fabrica: sessionmaker[Session]) -> None:
    partes = Partes()
    with fabrica.begin() as sessao:
        gestora = _inserir_base(sessao)
        pedido = PedidoDeEncaminhamento(CHAVE, Orgao.EMLURB, gestora)
        EncaminharOcorrencia(partes.servicos(sessao)).executar(pedido)
    partes.relogio.avancar(timedelta(days=DIAS_PARA_O_ORGAO_RESPONDER + 1))

    with fabrica.begin() as sessao:
        primeira = LembrarOrgaos(partes.servicos(sessao)).executar()
    with fabrica.begin() as sessao:
        segunda = LembrarOrgaos(partes.servicos(sessao)).executar()
        guardado = EncaminhamentoRepositorySql(sessao).buscar(1)

    assert (primeira.enviados, segunda.enviados) == (1, 0)
    assert guardado is not None
    assert guardado.lembrete_enviado_em is not None
