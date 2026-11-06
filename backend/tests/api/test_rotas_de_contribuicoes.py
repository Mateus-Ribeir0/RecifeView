from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencias import obter_registro_de_consultas, obter_usuario_atual
from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.domain.auditoria import ConsultaAuditada
from app.infrastructure.settings import Configuracao
from app.main import criar_aplicacao
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import criar_usuario
from tests.fakes_importacao import (
    ContribuicoesEmMemoria,
    LimiteFalso,
    TabelaFalsa,
    criar_servicos,
    criar_servicos_de_contribuicoes,
)

BASE = "/api/v1/contribuicoes"
ENVIO = {
    "chave_de_envio": "a" * 16,
    "servico_codigo": "131",
    "bairro_oficial": "AFOGADOS",
    "logradouro": "Rua da Esperança Fictícia",
    "numero": "100",
    "detalhe": "",
    "retorno": "nao_registrou",
}


class ConsultasSemEfeito:
    def registrar(self, consulta: ConsultaAuditada) -> None:
        return None


@pytest.fixture
def servicos() -> ServicosDeContribuicoes:
    return criar_servicos_de_contribuicoes(criar_servicos(TabelaFalsa([], [])))


def montar_cliente(servicos: ServicosDeContribuicoes) -> TestClient:
    app = criar_aplicacao(
        Configuracao(
            url_do_banco="postgresql+psycopg://u:s@localhost/inexistente",
            segredo_jwt=SecretStr(SEGREDO_DE_TESTE),
        )
    )
    app.state.servicos_de_importacao = servicos.importacao
    app.state.servicos_de_contribuicoes = servicos
    app.dependency_overrides[obter_registro_de_consultas] = ConsultasSemEfeito
    return TestClient(app)


@pytest.fixture
def cliente(servicos: ServicosDeContribuicoes) -> Iterator[TestClient]:
    with montar_cliente(servicos) as testes:
        yield testes


def entrar_como_gestor(cliente: TestClient) -> None:
    gestor = criar_usuario()
    cliente.app.dependency_overrides[obter_usuario_atual] = lambda: gestor  # type: ignore[attr-defined]


def test_catalogo_e_publico(cliente: TestClient) -> None:
    resposta = cliente.get(f"{BASE}/catalogo")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["bairros"][0]["chave"] == "AFOGADOS"
    assert corpo["temas"][0]["servicos"][0]["rotulo"] == "Lâmpada apagada"


def test_lista_vias_do_bairro(cliente: TestClient) -> None:
    resposta = cliente.get(f"{BASE}/logradouros", params={"bairro": "AFOGADOS"})

    assert resposta.json() == ["RUA DA ESPERANCA FICTICIA"]


def test_envio_publico_nao_exige_sessao(cliente: TestClient) -> None:
    resposta = cliente.post(BASE, json=ENVIO)

    assert resposta.status_code == 201
    assert resposta.json() == {"resultado": "nova"}


def test_resposta_do_envio_nao_revela_relato_de_outra_pessoa(cliente: TestClient) -> None:
    cliente.post(BASE, json=ENVIO)

    resposta = cliente.post(BASE, json={**ENVIO, "chave_de_envio": "b" * 16})

    assert resposta.json() == {"resultado": "somada"}


def test_robo_preenche_o_campo_escondido_e_nada_e_guardado(
    cliente: TestClient, servicos: ServicosDeContribuicoes
) -> None:
    resposta = cliente.post(BASE, json={**ENVIO, "site": "http://spam.exemplo"})

    assert resposta.status_code == 201
    assert cast(ContribuicoesEmMemoria, servicos.contribuicoes).itens == []


def test_dado_pessoal_volta_com_o_campo_certo(cliente: TestClient) -> None:
    resposta = cliente.post(BASE, json={**ENVIO, "detalhe": "ligue (81) 99999-1234"})

    assert resposta.status_code == 422
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "contribuicao_invalida"
    assert erro["detalhes"]["campo"] == "detalhe"
    assert "99999" not in erro["mensagem"]


def test_limite_de_envios_responde_429(
    cliente: TestClient, servicos: ServicosDeContribuicoes
) -> None:
    cast(LimiteFalso, servicos.limite).aberto = False

    resposta = cliente.post(BASE, json=ENVIO)

    assert resposta.status_code == 429


@pytest.mark.parametrize("caminho", ["/resumo", "/ocorrencias", "/pares"])
def test_rotas_da_gestao_exigem_sessao(cliente: TestClient, caminho: str) -> None:
    assert cliente.get(f"{BASE}{caminho}").status_code == 401


def test_decidir_e_gerar_pacote_exigem_sessao(cliente: TestClient) -> None:
    assert cliente.put(f"{BASE}/pares/1", json={"decisao": "mesma"}).status_code == 401
    assert cliente.post(f"{BASE}/pacotes").status_code == 401


def test_gestor_ve_o_resumo(cliente: TestClient) -> None:
    entrar_como_gestor(cliente)
    cliente.post(BASE, json=ENVIO)

    resposta = cliente.get(f"{BASE}/resumo")

    assert resposta.status_code == 200
    assert resposta.json()["relatos"] == 1


def test_pacote_vazio_responde_409(cliente: TestClient) -> None:
    entrar_como_gestor(cliente)

    resposta = cliente.post(f"{BASE}/pacotes")

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "pacote_vazio"
