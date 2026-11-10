from collections.abc import Iterator
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencias import (
    Repositorios,
    Seguranca,
    obter_bairros_oficiais,
    obter_registro_de_consultas,
    obter_repositorios,
    obter_seguranca,
    obter_servicos_de_conta,
)
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.application.sessoes import GestaoDeSessoes
from app.domain.auditoria import ConsultaAuditada
from app.domain.email import Email
from app.domain.usuario import Perfil, Usuario
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.settings import Configuracao
from app.main import criar_aplicacao
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import (
    SENHA_DE_TESTE,
    AcessosEmMemoria,
    CaixaDeEmailsEmMemoria,
    CodigosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)
from tests.fakes_importacao import TabelaFalsa, criar_servicos, criar_servicos_de_contribuicoes

BASE = "/api/v1"
EMAIL_DO_CIDADAO = "morador@exemplo.com"
EMAIL_DA_GESTORA = "gestora@recife.pe.gov.br"
SENHA_NOVA = "uma senha bem comprida"
ROTAS_DA_GESTAO = [
    ("get", "/indicadores/visao-geral"),
    ("get", "/war-room/calendario"),
    ("get", "/prioridade/criterios"),
    ("get", "/importacoes"),
    ("get", "/importacoes/campos"),
    ("post", "/importacoes/1/confirmar"),
    ("get", "/contribuicoes/resumo"),
    ("get", "/contribuicoes/pares"),
    ("post", "/contribuicoes/pacotes"),
]


class ConsultasSemEfeito:
    def registrar(self, consulta: ConsultaAuditada) -> None:
        return None


class Ambiente:
    def __init__(self) -> None:
        self.relogio = RelogioFixo()
        self.cidadao = criar_usuario(
            email=Email(EMAIL_DO_CIDADAO),
            perfil=Perfil.CIDADAO,
            email_confirmado_em=self.relogio.agora(),
        )
        self.gestora = criar_usuario(email=Email(EMAIL_DA_GESTORA))
        self.usuarios = UsuariosEmMemoria(self.cidadao, self.gestora)
        self.sessoes = SessoesEmMemoria()
        self.acessos = AcessosEmMemoria()
        self.emails = CaixaDeEmailsEmMemoria()
        self.codigos = CodigosEmMemoria()
        self.emissor = EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15))

    def servicos_de_conta(self) -> ServicosDeConta:
        return ServicosDeConta(
            usuarios=self.usuarios,
            codigos=self.codigos,
            senhas=HashDeSenhaDeTeste(),
            emails=self.emails,
            acessos=self.acessos,
            sessoes=GestaoDeSessoes(self.sessoes, self.emissor, self.relogio),
            relogio=self.relogio,
        )

    def montar(self) -> FastAPI:
        app = criar_aplicacao(
            Configuracao(
                url_do_banco="postgresql+psycopg://teste@localhost/nao-usado",
                segredo_jwt=SecretStr(SEGREDO_DE_TESTE),
                cookie_seguro=False,
            )
        )
        app.state.servicos_de_importacao = criar_servicos(TabelaFalsa([], []))
        app.state.servicos_de_contribuicoes = criar_servicos_de_contribuicoes(
            app.state.servicos_de_importacao
        )
        repositorios = Repositorios(self.usuarios, self.sessoes, self.acessos)
        seguranca = Seguranca(HashDeSenhaDeTeste(), self.emissor, self.relogio, timedelta(hours=12))
        app.dependency_overrides[obter_repositorios] = lambda: repositorios
        app.dependency_overrides[obter_seguranca] = lambda: seguranca
        app.dependency_overrides[obter_servicos_de_conta] = self.servicos_de_conta
        app.dependency_overrides[obter_bairros_oficiais] = lambda: frozenset({"AFOGADOS"})
        app.dependency_overrides[obter_registro_de_consultas] = ConsultasSemEfeito
        return app


@pytest.fixture
def ambiente() -> Ambiente:
    return Ambiente()


@pytest.fixture
def cliente(ambiente: Ambiente) -> Iterator[TestClient]:
    with TestClient(ambiente.montar()) as testes:
        yield testes


def token_de(cliente: TestClient, usuario: Usuario, area: str = "cidade") -> str:
    resposta = cliente.post(
        f"{BASE}/autenticacao/entrar",
        json={"email": str(usuario.email), "senha": SENHA_DE_TESTE, "area": area},
    )
    assert resposta.status_code == 200, resposta.text
    token: str = resposta.json()["token_de_acesso"]
    return token


@pytest.mark.parametrize(("metodo", "caminho"), ROTAS_DA_GESTAO)
def test_cidadao_recebe_403_em_toda_rota_da_gestao(
    cliente: TestClient, ambiente: Ambiente, metodo: str, caminho: str
) -> None:
    cabecalho = {"Authorization": f"Bearer {token_de(cliente, ambiente.cidadao)}"}

    resposta = cliente.request(metodo, f"{BASE}{caminho}", headers=cabecalho)

    assert resposta.status_code == 403
    assert resposta.json()["erro"]["codigo"] == "acesso_negado"


def test_cidadao_ve_os_relatos_da_cidade(cliente: TestClient, ambiente: Ambiente) -> None:
    cabecalho = {"Authorization": f"Bearer {token_de(cliente, ambiente.cidadao)}"}

    resposta = cliente.get(f"{BASE}/cidade/ocorrencias", headers=cabecalho)

    assert resposta.status_code == 200


def test_relatos_da_cidade_exigem_conta(cliente: TestClient) -> None:
    assert cliente.get(f"{BASE}/cidade/ocorrencias").status_code == 401


def test_gestora_tambem_ve_a_area_do_cidadao(cliente: TestClient, ambiente: Ambiente) -> None:
    cabecalho = {"Authorization": f"Bearer {token_de(cliente, ambiente.gestora, 'gestao')}"}

    assert cliente.get(f"{BASE}/cidade/ocorrencias", headers=cabecalho).status_code == 200


def test_cidadao_nao_entra_pela_porta_da_gestao(cliente: TestClient, ambiente: Ambiente) -> None:
    resposta = cliente.post(
        f"{BASE}/autenticacao/entrar",
        json={"email": EMAIL_DO_CIDADAO, "senha": SENHA_DE_TESTE, "area": "gestao"},
    )

    assert resposta.status_code == 403
    assert resposta.json()["erro"]["codigo"] == "area_da_gestao_negada"


def cadastrar(cliente: TestClient, **mudancas: object) -> dict[str, object]:
    dados = {
        "nome": "Maria da Silva",
        "email": "nova@exemplo.com",
        "senha": SENHA_NOVA,
        "bairro_oficial": "AFOGADOS",
        "aceitou_os_termos": True,
        **mudancas,
    }
    resposta = cliente.post(f"{BASE}/contas", json=dados)
    assert resposta.status_code == 202, resposta.text
    corpo: dict[str, object] = resposta.json()
    return corpo


def test_cadastro_responde_igual_para_email_novo_e_usado(cliente: TestClient) -> None:
    novo = cadastrar(cliente)
    usado = cadastrar(cliente, email=EMAIL_DA_GESTORA)

    assert novo == usado


def test_cadastro_confirmacao_e_entrada(cliente: TestClient, ambiente: Ambiente) -> None:
    cadastrar(cliente)
    pendente = cliente.post(
        f"{BASE}/autenticacao/entrar", json={"email": "nova@exemplo.com", "senha": SENHA_NOVA}
    )
    assert pendente.json()["erro"]["codigo"] == "email_nao_confirmado"

    confirmacao = cliente.post(
        f"{BASE}/contas/confirmar",
        json={
            "email": "nova@exemplo.com",
            "codigo": ambiente.emails.ultimo_codigo(),
            "senha": SENHA_NOVA,
        },
    )

    assert confirmacao.status_code == 200
    usuario = confirmacao.json()["usuario"]
    assert usuario["perfil"] == "CIDADAO"
    assert usuario["bairro_oficial"] == "AFOGADOS"
    assert "set-cookie" in confirmacao.headers


def test_robo_no_campo_escondido_nao_cria_conta(cliente: TestClient, ambiente: Ambiente) -> None:
    cadastrar(cliente, site="http://spam.exemplo")

    assert ambiente.usuarios.buscar_por_email(Email("nova@exemplo.com")) is None
    assert ambiente.emails.mensagens == []


def test_campo_invalido_volta_com_o_nome_do_campo(cliente: TestClient) -> None:
    resposta = cliente.post(
        f"{BASE}/contas",
        json={
            "nome": "Maria 123",
            "email": "nova@exemplo.com",
            "senha": SENHA_NOVA,
            "aceitou_os_termos": True,
        },
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["detalhes"] == {"campo": "nome"}


def test_codigo_fora_do_formato_e_recusado_antes_de_conferir(cliente: TestClient) -> None:
    resposta = cliente.post(
        f"{BASE}/contas/confirmar",
        json={"email": "nova@exemplo.com", "codigo": "12ab56", "senha": SENHA_NOVA},
    )
    assert resposta.status_code == 422


def test_limite_de_operacoes_de_conta(cliente: TestClient) -> None:
    respostas = [
        cliente.post(f"{BASE}/contas/reenviar-codigo", json={"email": "x@exemplo.com"})
        for _ in range(11)
    ]

    assert respostas[-1].status_code == 429
    assert respostas[-1].json()["erro"]["codigo"] == "tentativas_demais"


def test_cidadao_exclui_a_propria_conta(cliente: TestClient, ambiente: Ambiente) -> None:
    cabecalho = {"Authorization": f"Bearer {token_de(cliente, ambiente.cidadao)}"}

    resposta = cliente.post(
        f"{BASE}/contas/eu/excluir", json={"senha": SENHA_DE_TESTE}, headers=cabecalho
    )

    assert resposta.status_code == 204
    assert ambiente.usuarios.buscar_por_email(Email(EMAIL_DO_CIDADAO)) is None
