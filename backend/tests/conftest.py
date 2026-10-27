from datetime import timedelta

import pytest

from app.application.sessoes import GestaoDeSessoes
from app.domain.usuario import Usuario
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from tests.fakes import (
    AcessosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)

SEGREDO_DE_TESTE = "segredo-de-teste-com-mais-de-trinta-e-dois-caracteres"


@pytest.fixture
def relogio() -> RelogioFixo:
    return RelogioFixo()


@pytest.fixture
def senhas() -> HashDeSenhaDeTeste:
    return HashDeSenhaDeTeste()


@pytest.fixture
def usuario() -> Usuario:
    return criar_usuario()


@pytest.fixture
def usuarios(usuario: Usuario) -> UsuariosEmMemoria:
    return UsuariosEmMemoria(usuario)


@pytest.fixture
def sessoes_em_memoria() -> SessoesEmMemoria:
    return SessoesEmMemoria()


@pytest.fixture
def acessos() -> AcessosEmMemoria:
    return AcessosEmMemoria()


@pytest.fixture
def emissor() -> EmissorDeTokenJwt:
    return EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15))


@pytest.fixture
def gestao_de_sessoes(
    sessoes_em_memoria: SessoesEmMemoria, emissor: EmissorDeTokenJwt, relogio: RelogioFixo
) -> GestaoDeSessoes:
    return GestaoDeSessoes(sessoes_em_memoria, emissor, relogio)
