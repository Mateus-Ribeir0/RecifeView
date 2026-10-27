from collections.abc import Iterator
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.cookies import NOME_DO_COOKIE_DE_SESSAO
from app.api.dependencias import Repositorios, Seguranca, obter_repositorios, obter_seguranca
from app.domain.usuario import TENTATIVAS_ANTES_DO_BLOQUEIO, Usuario
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.settings import Configuracao
from app.main import criar_aplicacao
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import (
    SENHA_DE_TESTE,
    AcessosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)

EMAIL = "gestora@recife.pe.gov.br"
ENTRAR = "/api/v1/autenticacao/entrar"
RENOVAR = "/api/v1/autenticacao/renovar"
SAIR = "/api/v1/autenticacao/sair"
EU = "/api/v1/autenticacao/eu"
TROCAR_SENHA = "/api/v1/autenticacao/trocar-senha"


def montar_aplicacao(usuario: Usuario, relogio: RelogioFixo) -> FastAPI:
    configuracao = Configuracao(
        url_do_banco="postgresql+psycopg://teste@localhost/nao-usado",
        segredo_jwt=SecretStr(SEGREDO_DE_TESTE),
        cookie_seguro=False,
    )
    app = criar_aplicacao(configuracao)
    repositorios = Repositorios(UsuariosEmMemoria(usuario), SessoesEmMemoria(), AcessosEmMemoria())
    seguranca = Seguranca(
        HashDeSenhaDeTeste(),
        EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15)),
        relogio,
        timedelta(hours=12),
    )
    app.dependency_overrides[obter_repositorios] = lambda: repositorios
    app.dependency_overrides[obter_seguranca] = lambda: seguranca
    return app


@pytest.fixture
def cliente(usuario: Usuario, relogio: RelogioFixo) -> Iterator[TestClient]:
    with TestClient(montar_aplicacao(usuario, relogio)) as cliente:
        yield cliente


def entrar(cliente: TestClient, senha: str = SENHA_DE_TESTE) -> str:
    resposta = cliente.post(ENTRAR, json={"email": EMAIL, "senha": senha})
    assert resposta.status_code == 200
    token: str = resposta.json()["token_de_acesso"]
    return token


def test_entrar_devolve_token_e_grava_cookie_de_sessao_protegido(cliente: TestClient) -> None:
    resposta = cliente.post(ENTRAR, json={"email": EMAIL, "senha": SENHA_DE_TESTE})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_de_acesso"]
    assert corpo["usuario"]["email"] == EMAIL
    assert "hash_da_senha" not in corpo["usuario"]
    cookie = resposta.headers["set-cookie"]
    assert cookie.startswith(f"{NOME_DO_COOKIE_DE_SESSAO}=")
    assert "HttpOnly" in cookie
    assert "SameSite=strict" in cookie
    assert "Path=/api/v1/autenticacao" in cookie


def test_senha_errada_responde_401_no_formato_padrao(cliente: TestClient) -> None:
    resposta = cliente.post(ENTRAR, json={"email": EMAIL, "senha": "errada"})
    assert resposta.status_code == 401
    assert resposta.json() == {
        "erro": {"codigo": "credenciais_invalidas", "mensagem": "E-mail ou senha incorretos."}
    }


def test_bloqueio_responde_429_com_horario_de_desbloqueio(cliente: TestClient) -> None:
    for _ in range(TENTATIVAS_ANTES_DO_BLOQUEIO - 1):
        cliente.post(ENTRAR, json={"email": EMAIL, "senha": "errada"})

    resposta = cliente.post(ENTRAR, json={"email": EMAIL, "senha": "errada"})

    assert resposta.status_code == 429
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "conta_bloqueada"
    assert "desbloqueio_em" in erro["detalhes"]


def test_campos_faltando_respondem_422_com_os_campos(cliente: TestClient) -> None:
    resposta = cliente.post(ENTRAR, json={"email": EMAIL})
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["detalhes"] == {"campos": ["senha"]}


def test_renovar_usa_o_cookie_de_sessao(cliente: TestClient) -> None:
    entrar(cliente)
    resposta = cliente.post(RENOVAR)
    assert resposta.status_code == 200
    assert resposta.json()["usuario"]["email"] == EMAIL


def test_renovar_sem_cookie_responde_401(cliente: TestClient) -> None:
    resposta = cliente.post(RENOVAR)
    assert resposta.status_code == 401
    assert resposta.json()["erro"]["codigo"] == "sessao_invalida"


def test_eu_exige_token_de_acesso(cliente: TestClient) -> None:
    assert cliente.get(EU).status_code == 401
    token = entrar(cliente)
    resposta = cliente.get(EU, headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Gestora de Teste"


def test_sair_apaga_o_cookie_e_impede_renovar(cliente: TestClient) -> None:
    entrar(cliente)
    resposta = cliente.post(SAIR)
    assert resposta.status_code == 204
    assert f'{NOME_DO_COOKIE_DE_SESSAO}=""' in resposta.headers["set-cookie"]
    assert cliente.post(RENOVAR).status_code == 401


def test_trocar_senha_no_primeiro_acesso(relogio: RelogioFixo) -> None:
    primeiro_acesso = criar_usuario(deve_trocar_senha=True)
    with TestClient(montar_aplicacao(primeiro_acesso, relogio)) as cliente:
        token = entrar(cliente)
        resposta = cliente.post(
            TROCAR_SENHA,
            json={"senha_atual": SENHA_DE_TESTE, "nova_senha": "ponte-boa-vista-1840"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resposta.status_code == 200
        assert resposta.json()["usuario"]["deve_trocar_senha"] is False


def test_nova_senha_fraca_explica_o_motivo(cliente: TestClient) -> None:
    token = entrar(cliente)
    resposta = cliente.post(
        TROCAR_SENHA,
        json={"senha_atual": SENHA_DE_TESTE, "nova_senha": "curtinha"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 422
    assert resposta.json()["erro"] == {
        "codigo": "senha_fraca",
        "mensagem": "A senha precisa ter pelo menos 12 caracteres.",
    }


def test_saude(cliente: TestClient) -> None:
    assert cliente.get("/api/v1/saude").json() == {"situacao": "ok"}
