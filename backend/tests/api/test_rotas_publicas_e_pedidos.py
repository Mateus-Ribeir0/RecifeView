from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencias import obter_servicos_de_pedidos
from app.application.casos_de_uso.pedidos.consultar_pedido import ConsultarPedido
from app.application.casos_de_uso.pedidos.meus_pedidos import ServicosDePedidos
from app.domain.pedido import RegistroDoPedido
from tests.api.test_rotas_de_contas_e_perfis import BASE, Ambiente, token_de
from tests.fakes import ConsultaDePedidosEmMemoria
from tests.fakes_encaminhamento import EncaminhamentosEmMemoria

REGISTRO = RegistroDoPedido(
    7, "OUVIDORIA", "2026/0001", servico="ILUMINACAO", situacao="EM ANDAMENTO"
)


@pytest.fixture
def ambiente() -> Ambiente:
    return Ambiente()


@pytest.fixture
def cliente(ambiente: Ambiente) -> Iterator[TestClient]:
    app = ambiente.montar()
    consultar = ConsultarPedido(ConsultaDePedidosEmMemoria(REGISTRO), EncaminhamentosEmMemoria())
    app.dependency_overrides[obter_servicos_de_pedidos] = lambda: ServicosDePedidos(
        consultar, ambiente.pedidos, ambiente.relogio
    )
    with TestClient(app) as testes:
        yield testes


def test_qualquer_pessoa_consulta_o_pedido_pelo_protocolo(cliente: TestClient) -> None:
    resposta = cliente.post(f"{BASE}/publico/pedidos/consultar", json={"protocolo": "2026/0001"})

    assert resposta.status_code == 200
    (andamento,) = resposta.json()
    assert andamento["rotulo_da_fonte"] == "Ouvidoria"
    assert andamento["situacao"] == "EM ANDAMENTO"
    assert andamento["encaminhamentos"] == []
    assert "id_local" not in andamento


def test_protocolo_fora_do_formato_volta_422(cliente: TestClient) -> None:
    resposta = cliente.post(f"{BASE}/publico/pedidos/consultar", json={"protocolo": "rua x, 1"})

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "protocolo_invalido"


def test_cidadao_guarda_lista_e_tira_um_pedido(cliente: TestClient, ambiente: Ambiente) -> None:
    cabecalho = {"Authorization": f"Bearer {token_de(cliente, ambiente.cidadao)}"}

    guardado = cliente.post(
        f"{BASE}/cidade/pedidos", json={"protocolo": "2026/0001"}, headers=cabecalho
    )
    lista = cliente.get(f"{BASE}/cidade/pedidos", headers=cabecalho)
    retirado = cliente.delete(f"{BASE}/cidade/pedidos/{guardado.json()['id']}", headers=cabecalho)

    assert guardado.status_code == 201
    assert lista.json()[0]["andamentos"][0]["servico"] == "ILUMINACAO"
    assert retirado.status_code == 204
    assert cliente.get(f"{BASE}/cidade/pedidos", headers=cabecalho).json() == []


def test_meus_pedidos_exige_conta(cliente: TestClient) -> None:
    assert cliente.get(f"{BASE}/cidade/pedidos").status_code == 401
