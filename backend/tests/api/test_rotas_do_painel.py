from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.dependencias import (
    Repositorios,
    Seguranca,
    obter_registro_de_consultas,
    obter_repositorios,
    obter_repositorios_do_painel,
    obter_seguranca,
    obter_usuario_atual,
)
from app.domain.auditoria import ConsultaAuditada
from app.domain.catalogos import CatalogoDeFiltros
from app.domain.filtros import Filtros
from app.domain.procedencia import Referencia
from app.domain.visao_geral import DemandaPorAno, PercentisDePrazo, ResumoDasIndicacoes
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.settings import Configuracao
from app.main import criar_aplicacao
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import (
    AcessosEmMemoria,
    HashDeSenhaDeTeste,
    RelogioFixo,
    SessoesEmMemoria,
    UsuariosEmMemoria,
    criar_usuario,
)
from tests.fakes_importacao import (
    TabelaFalsa,
    criar_servicos,
    criar_servicos_de_contribuicoes,
)

BASE = "/api/v1"
COLUNAS_PROIBIDAS = ("texto", "id_local", "logradouro", "lat", "lon", "referencia", "ementa")


class IndicadoresFalsos:
    def __init__(self) -> None:
        self.filtros: list[Filtros] = []

    def demandas_por_ano(self, filtros: Filtros) -> list[DemandaPorAno]:
        self.filtros.append(filtros)
        return [DemandaPorAno(2024, "156_EMLURB", 10), DemandaPorAno(2024, "OUVIDORIA", 5)]

    def resumo_das_indicacoes(self, filtros: Filtros) -> ResumoDasIndicacoes:
        return ResumoDasIndicacoes(100, 97, 21, 9.0, 241.0)

    def pct_local_repetido(self, filtros: Filtros) -> float | None:
        return 52.0

    def percentis_de_prazo(self, filtros: Filtros) -> PercentisDePrazo:
        return PercentisDePrazo(4, 60)


class ReferenciaFalsa:
    def atual(self) -> Referencia:
        return Referencia(date(2026, 10, 7), datetime(2026, 11, 5, tzinfo=UTC))


class CatalogoFalso:
    def filtros(self) -> CatalogoDeFiltros:
        return CatalogoDeFiltros(2012, 2026, ["1"], [], ["DRENAGEM"], [])


class ConsultasFalsas:
    def __init__(self) -> None:
        self.registradas: list[ConsultaAuditada] = []

    def registrar(self, consulta: ConsultaAuditada) -> None:
        self.registradas.append(consulta)


@pytest.fixture
def consultas() -> ConsultasFalsas:
    return ConsultasFalsas()


@pytest.fixture
def indicadores() -> IndicadoresFalsos:
    return IndicadoresFalsos()


def montar(consultas: ConsultasFalsas, indicadores: IndicadoresFalsos) -> FastAPI:
    configuracao = Configuracao(
        url_do_banco="postgresql+psycopg://teste@localhost/nao-usado",
        segredo_jwt=SecretStr(SEGREDO_DE_TESTE),
        cookie_seguro=False,
    )
    app = criar_aplicacao(configuracao)
    app.state.servicos_de_importacao = criar_servicos(TabelaFalsa([], []))
    app.state.servicos_de_contribuicoes = criar_servicos_de_contribuicoes(
        app.state.servicos_de_importacao
    )
    painel = SimpleNamespace(
        catalogo=CatalogoFalso(), referencia=ReferenciaFalsa(), visao_geral=indicadores
    )
    usuario = criar_usuario()
    seguranca = Seguranca(
        HashDeSenhaDeTeste(),
        EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15)),
        RelogioFixo(),
        timedelta(hours=12),
    )
    repositorios = Repositorios(UsuariosEmMemoria(usuario), SessoesEmMemoria(), AcessosEmMemoria())
    app.dependency_overrides[obter_repositorios] = lambda: repositorios
    app.dependency_overrides[obter_seguranca] = lambda: seguranca
    app.dependency_overrides[obter_repositorios_do_painel] = lambda: painel
    app.dependency_overrides[obter_registro_de_consultas] = lambda: consultas
    app.dependency_overrides[obter_usuario_atual] = lambda: usuario
    return app


@pytest.fixture
def cliente(consultas: ConsultasFalsas, indicadores: IndicadoresFalsos) -> Iterator[TestClient]:
    with TestClient(montar(consultas, indicadores)) as cliente_de_teste:
        yield cliente_de_teste


def chaves_de(valor: Any) -> set[str]:
    if isinstance(valor, dict):
        return set(valor) | {chave for item in valor.values() for chave in chaves_de(item)}
    if isinstance(valor, list):
        return {chave for item in valor for chave in chaves_de(item)}
    return set()


def test_rota_de_dados_exige_sessao(
    consultas: ConsultasFalsas, indicadores: IndicadoresFalsos
) -> None:
    app = montar(consultas, indicadores)
    del app.dependency_overrides[obter_usuario_atual]

    with TestClient(app) as sem_sessao:
        resposta = sem_sessao.get(f"{BASE}/indicadores/visao-geral")

    assert resposta.status_code == 401
    assert resposta.json()["erro"]["codigo"] == "sessao_invalida"


def test_visao_geral_traz_dados_e_procedencia(cliente: TestClient) -> None:
    corpo = cliente.get(f"{BASE}/indicadores/visao-geral").json()

    assert corpo["dados"]["demandas"] == 15
    assert corpo["dados"]["indicacoes"]["pct_enviadas"] == 97
    assert corpo["dados"]["prazo"] == {"mediana": 4, "p90": 60}
    assert corpo["meta"]["periodo"] == {"inicio": 2021, "fim": 2025}
    assert corpo["meta"]["n"] == 15
    assert "156_EMLURB" in corpo["meta"]["fonte"]


def test_filtros_da_url_chegam_ao_caso_de_uso(
    cliente: TestClient, indicadores: IndicadoresFalsos
) -> None:
    cliente.get(
        f"{BASE}/indicadores/visao-geral",
        params={
            "periodo_inicio": "2015-01",
            "periodo_fim": "2020-12",
            "rpa": ["1", "2"],
            "bairro": "AFOGADOS",
            "categoria": "DRENAGEM",
        },
    )

    assert indicadores.filtros[0] == Filtros(2015, 2020, ("1", "2"), ("AFOGADOS",), ("DRENAGEM",))


def test_periodo_invertido_devolve_erro_com_codigo(cliente: TestClient) -> None:
    resposta = cliente.get(
        f"{BASE}/indicadores/visao-geral",
        params={"periodo_inicio": "2025-01", "periodo_fim": "2021-12"},
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "periodo_invalido"


def test_periodo_fora_do_formato_e_recusado(cliente: TestClient) -> None:
    resposta = cliente.get(f"{BASE}/indicadores/visao-geral", params={"periodo_inicio": "2021"})

    assert resposta.status_code == 422


def test_consulta_fica_auditada_com_filtros(
    cliente: TestClient, consultas: ConsultasFalsas
) -> None:
    cliente.get(f"{BASE}/indicadores/visao-geral", params={"rpa": ["3"]})

    registrada = consultas.registradas[0]
    assert registrada.rota == f"{BASE}/indicadores/visao-geral"
    assert registrada.filtros == {"rpa": ["3"]}


def test_catalogo_lista_as_opcoes_dos_filtros(cliente: TestClient) -> None:
    corpo = cliente.get(f"{BASE}/catalogos/filtros").json()

    assert corpo["ano_maximo"] == 2026
    assert corpo["categorias"] == ["DRENAGEM"]


def test_criterios_trazem_os_julgamentos_do_grupo(cliente: TestClient) -> None:
    corpo = cliente.get(f"{BASE}/prioridade/criterios").json()

    assert corpo["criterios"][0]["chave"] == "risco"
    assert len(corpo["julgamentos_padrao"]) == 6


def test_julgamento_entre_criterios_inexistentes_e_recusado(cliente: TestClient) -> None:
    resposta = cliente.post(
        f"{BASE}/prioridade/indice",
        json={"julgamentos": [{"primeiro": "risco", "segundo": "beleza", "valor": 2}]},
    )

    assert resposta.status_code == 422


def test_julgamento_fora_da_escala_de_saaty_e_recusado(cliente: TestClient) -> None:
    resposta = cliente.post(
        f"{BASE}/prioridade/indice",
        json={"julgamentos": [{"primeiro": "risco", "segundo": "atraso", "valor": 40}]},
    )

    assert resposta.status_code == 422


def test_importacao_nao_expoe_referencia_nem_valor_de_coluna_bloqueada(
    consultas: ConsultasFalsas, indicadores: IndicadoresFalsos
) -> None:
    colunas = ["GRUPOSERVICO_DESCRICAO", "DATA_DEMANDA", "LOGRADOURO", "CPF"]
    linhas = [["DRENAGEM", "2026-02-10", "RUA DO TESTE", "123.456.789-09"]]
    app = montar(consultas, indicadores)
    app.state.servicos_de_importacao = criar_servicos(TabelaFalsa(colunas, linhas))
    app.state.servicos_de_contribuicoes = criar_servicos_de_contribuicoes(
        app.state.servicos_de_importacao
    )

    with TestClient(app) as cliente_de_teste:
        criada = cliente_de_teste.post(
            f"{BASE}/importacoes", params={"nome": "156.csv"}, content=b"qualquer"
        ).json()
        detalhe = cliente_de_teste.get(f"{BASE}/importacoes/{criada['id']}")

    assert detalhe.status_code == 200
    assert "RUA DO TESTE" not in detalhe.text
    assert "123.456" not in detalhe.text
    assert not chaves_de(detalhe.json()) & set(COLUNAS_PROIBIDAS)


def test_importacao_inexistente_devolve_404(cliente: TestClient) -> None:
    resposta = cliente.get(f"{BASE}/importacoes/999")

    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "importacao_nao_encontrada"
