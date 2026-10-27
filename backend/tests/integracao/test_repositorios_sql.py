from collections.abc import Iterator
from datetime import timedelta
from uuid import uuid4

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.email import Email
from app.domain.sessao import Sessao
from app.infrastructure.db.base import ESQUEMA_DA_APLICACAO, Base
from app.infrastructure.db.modelos import EventoDeAcessoModelo
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from tests.fakes import INICIO_DOS_TESTES, criar_usuario


class ConfiguracaoDosTestes(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    url_do_banco_de_teste: str | None = None


URL_DO_BANCO_DE_TESTE = ConfiguracaoDosTestes().url_do_banco_de_teste

pytestmark = pytest.mark.skipif(
    not URL_DO_BANCO_DE_TESTE, reason="API_URL_DO_BANCO_DE_TESTE não definida"
)


@pytest.fixture
def sessao_do_banco() -> Iterator[Session]:
    assert URL_DO_BANCO_DE_TESTE
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    with motor.begin() as conexao:
        conexao.execute(text(f"DROP SCHEMA IF EXISTS {ESQUEMA_DA_APLICACAO} CASCADE"))
        conexao.execute(text(f"CREATE SCHEMA {ESQUEMA_DA_APLICACAO}"))
        Base.metadata.create_all(conexao)
    with Session(motor) as sessao:
        yield sessao
    motor.dispose()


def test_usuario_ida_e_volta(sessao_do_banco: Session) -> None:
    repositorio = UsuarioRepositorySql(sessao_do_banco)
    usuario = criar_usuario(bloqueado_ate=INICIO_DOS_TESTES)

    repositorio.adicionar(usuario)
    sessao_do_banco.commit()

    assert repositorio.buscar_por_email(Email("GESTORA@recife.pe.gov.br")) == usuario
    assert repositorio.buscar_por_id(usuario.id) == usuario


def test_atualizar_usuario_grava_tentativas(sessao_do_banco: Session) -> None:
    repositorio = UsuarioRepositorySql(sessao_do_banco)
    usuario = criar_usuario()
    repositorio.adicionar(usuario)

    repositorio.atualizar(usuario.com_falha_de_entrada(INICIO_DOS_TESTES))
    sessao_do_banco.commit()

    salvo = repositorio.buscar_por_id(usuario.id)
    assert salvo is not None
    assert salvo.tentativas_falhas == 1


def test_sessoes_revogadas_em_lote(sessao_do_banco: Session) -> None:
    usuario = criar_usuario()
    UsuarioRepositorySql(sessao_do_banco).adicionar(usuario)
    repositorio = SessaoRepositorySql(sessao_do_banco)
    for indice in range(2):
        repositorio.adicionar(
            Sessao(
                id=uuid4(),
                usuario_id=usuario.id,
                hash_do_token=f"{indice:064d}",
                criada_em=INICIO_DOS_TESTES,
                expira_em=INICIO_DOS_TESTES + timedelta(hours=12),
            )
        )

    repositorio.revogar_todas_do_usuario(usuario.id, INICIO_DOS_TESTES)
    sessao_do_banco.commit()

    sessao = repositorio.buscar_por_hash_do_token(f"{0:064d}")
    assert sessao is not None
    assert sessao.revogada_em == INICIO_DOS_TESTES


def test_evento_de_acesso_sem_usuario(sessao_do_banco: Session) -> None:
    RegistroDeAcessosSql(sessao_do_banco).registrar(
        EventoDeAcesso(TipoDeEventoDeAcesso.ENTRADA_RECUSADA, INICIO_DOS_TESTES)
    )
    sessao_do_banco.commit()

    evento = sessao_do_banco.scalar(select(EventoDeAcessoModelo))
    assert evento is not None
    assert evento.usuario_id is None
    assert evento.tipo == "ENTRADA_RECUSADA"
