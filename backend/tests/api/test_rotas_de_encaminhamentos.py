from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencias import obter_servicos_de_encaminhamento
from tests.api.test_rotas_de_contas_e_perfis import BASE, Ambiente, token_de
from tests.fakes_encaminhamento import (
    DespachoEmMemoria,
    EncaminhamentosEmMemoria,
    criar_servicos_de_encaminhamento,
    ocorrencia_de_teste,
)


class AmbienteComEncaminhamentos(Ambiente):
    def __init__(self) -> None:
        super().__init__()
        self.repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste(7, protocolo="2026/9"))
        self.despacho = DespachoEmMemoria()


@pytest.fixture
def ambiente() -> AmbienteComEncaminhamentos:
    return AmbienteComEncaminhamentos()


@pytest.fixture
def cliente(ambiente: AmbienteComEncaminhamentos) -> Iterator[TestClient]:
    app = ambiente.montar()
    app.dependency_overrides[obter_servicos_de_encaminhamento] = lambda: (
        criar_servicos_de_encaminhamento(ambiente.repositorio, ambiente.despacho, ambiente.relogio)
    )
    with TestClient(app) as testes:
        yield testes


def cabecalho_da_gestora(cliente: TestClient, ambiente: Ambiente) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_de(cliente, ambiente.gestora, 'gestao')}"}


def encaminhar(cliente: TestClient, ambiente: Ambiente) -> dict[str, object]:
    resposta = cliente.post(
        f"{BASE}/encaminhamentos",
        json={"chave_registro": 7, "orgao": "COMPESA", "justificativa": "Terceira vez no mês"},
        headers=cabecalho_da_gestora(cliente, ambiente),
    )
    assert resposta.status_code == 201, resposta.text
    corpo: dict[str, object] = resposta.json()
    return corpo


def test_gestora_ve_a_sugestao_antes_de_encaminhar(
    cliente: TestClient, ambiente: AmbienteComEncaminhamentos
) -> None:
    resposta = cliente.get(
        f"{BASE}/encaminhamentos/ocorrencias/7", headers=cabecalho_da_gestora(cliente, ambiente)
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["sugestao"]["orgao"] == "EMLURB"
    assert corpo["sugestao"]["motivo"] == "apontado_no_registro"
    assert corpo["pode_encaminhar"] is True
    assert {orgao["orgao"] for orgao in corpo["orgaos"]} >= {"COMPESA", "NEOENERGIA"}


def test_encaminhamento_sai_com_codigo_e_entra_na_lista(
    cliente: TestClient, ambiente: AmbienteComEncaminhamentos
) -> None:
    encaminhamento = encaminhar(cliente, ambiente)

    lista = cliente.get(f"{BASE}/encaminhamentos", headers=cabecalho_da_gestora(cliente, ambiente))

    assert encaminhamento["codigo"] == "ENC-2026-000001"
    assert encaminhamento["situacao"] == "enviado"
    assert lista.json()["total"] == 1
    assert ambiente.despacho.enviadas[0].dados["protocolo_de_origem"] == "2026/9"


def test_segundo_encaminhamento_aberto_e_recusado(
    cliente: TestClient, ambiente: AmbienteComEncaminhamentos
) -> None:
    encaminhar(cliente, ambiente)

    resposta = cliente.post(
        f"{BASE}/encaminhamentos",
        json={"chave_registro": 7, "orgao": "EMLURB"},
        headers=cabecalho_da_gestora(cliente, ambiente),
    )

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "ocorrencia_ja_encaminhada"


def test_orgao_abre_e_responde_pelo_link_sem_sessao(
    cliente: TestClient, ambiente: AmbienteComEncaminhamentos
) -> None:
    encaminhar(cliente, ambiente)
    token = ambiente.despacho.ultimo_token()

    aberto = cliente.post(f"{BASE}/retornos/abrir", json={"token": token})
    resposta = cliente.post(
        f"{BASE}/retornos",
        json={"token": token, "situacao": "recebido", "protocolo_do_orgao": "CMP-55"},
    )

    assert aberto.status_code == 200
    assert aberto.json()["respostas_possiveis"] == ["recebido", "resolvido", "devolvido"]
    assert resposta.status_code == 200
    assert resposta.json()["situacao"] == "recebido"
    assert resposta.json()["respostas_possiveis"] == ["resolvido", "devolvido"]


def test_link_desconhecido_responde_404(cliente: TestClient) -> None:
    resposta = cliente.post(f"{BASE}/retornos/abrir", json={"token": "nao-existe"})

    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "link_de_retorno_invalido"


def test_observacao_com_telefone_e_recusada(
    cliente: TestClient, ambiente: AmbienteComEncaminhamentos
) -> None:
    encaminhar(cliente, ambiente)

    resposta = cliente.post(
        f"{BASE}/retornos",
        json={
            "token": ambiente.despacho.ultimo_token(),
            "situacao": "resolvido",
            "observacao": "Fale com o fiscal no (81) 98888-7777",
        },
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["detalhes"]["campo"] == "observacao"
