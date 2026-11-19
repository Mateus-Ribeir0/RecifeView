from collections.abc import Iterator
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencias import obter_servicos_de_pedidos
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.retorno import (
    RegistrarRetornoPelaGestao,
    RespostaAoEncaminhamento,
)
from app.application.casos_de_uso.pedidos.consultar_pedido import ConsultarPedido
from app.application.casos_de_uso.pedidos.meus_pedidos import ServicosDePedidos
from app.domain.encaminhamento.encaminhamento import SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.pedido import RegistroDoPedido
from tests.api.test_rotas_de_contas_e_perfis import BASE, Ambiente, token_de
from tests.fakes import ConsultaDePedidosEmMemoria
from tests.fakes_encaminhamento import Ambiente as CicloEmMemoria
from tests.fakes_encaminhamento import EncaminhamentosEmMemoria, ocorrencia_de_teste

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


def test_consulta_mostra_a_resposta_ao_cidadao_e_nunca_a_nota_interna(
    ambiente: Ambiente,
) -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste(7, protocolo="2026/0001"))
    ciclo = CicloEmMemoria(repositorio, relogio=ambiente.relogio)
    pedido = PedidoDeEncaminhamento(7, Orgao.EMLURB, uuid4())
    encaminhado = EncaminharOcorrencia(ciclo.servicos()).executar(pedido)
    hoje = ambiente.relogio.agora().date()
    atendimento = RespostaAoEncaminhamento(
        SituacaoDoEncaminhamento.RECEBIDO,
        observacao="Equipe B, ordem interna 77",
        resposta_ao_cidadao="A equipe vai ao local nesta semana",
        previsao=hoje + timedelta(days=5),
    )
    RegistrarRetornoPelaGestao(ciclo.servicos()).executar(encaminhado.id, atendimento, uuid4())
    app = ambiente.montar()
    consultar = ConsultarPedido(ConsultaDePedidosEmMemoria(REGISTRO), repositorio)
    app.dependency_overrides[obter_servicos_de_pedidos] = lambda: ServicosDePedidos(
        consultar, ambiente.pedidos, ambiente.relogio
    )
    with TestClient(app) as cliente:
        resposta = cliente.post(
            f"{BASE}/publico/pedidos/consultar", json={"protocolo": "2026/0001"}
        )

    (encaminhamento,) = resposta.json()[0]["encaminhamentos"]
    assert encaminhamento["resposta_do_orgao"] == "A equipe vai ao local nesta semana"
    assert encaminhamento["previsao"] == (hoje + timedelta(days=5)).isoformat()
    assert "ordem interna" not in resposta.text
