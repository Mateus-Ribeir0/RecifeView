from datetime import date, timedelta
from typing import Any

from sqlalchemy import Row, text
from sqlalchemy.orm import Session

from app.application.portas.indicadores import OpcoesDeFiltro
from app.domain.encaminhamento.desempenho import (
    DIAS_PARA_VOLTAR_A_SER_PEDIDO,
    SEMANAS_NA_SERIE,
    ContagemPorTema,
    IndicadoresDoOrgao,
    SemanaDoCiclo,
)
from app.domain.encaminhamento.orgaos import Orgao

DIAS_DAS_RESOLVIDAS_RECENTES = 30
TEMAS_RESOLVIDOS_MOSTRADOS = 8
SEM_TEMA = "SEM TEMA"
DO_ORGAO = "(CAST(:orgao AS text) IS NULL OR e.orgao = :orgao)"

POR_ORGAO = f"""
WITH resolucao AS (
    SELECT encaminhamento_id, min(ocorrido_em) AS resolvido_em
    FROM app.evento_de_encaminhamento
    WHERE situacao = 'resolvido'
    GROUP BY encaminhamento_id
),
base AS (
    SELECT e.*, r.resolvido_em
    FROM app.encaminhamento e
    LEFT JOIN resolucao r ON r.encaminhamento_id = e.id
    WHERE {DO_ORGAO}
),
voltaram AS (
    SELECT DISTINCT b.id
    FROM base b
    JOIN ouro.fato_demanda f
        ON f.fonte = b.fonte AND f.id_local = b.id_local AND f.categoria = b.categoria
        AND f.data_abertura > b.resolvido_em::date
        AND f.data_abertura <= b.resolvido_em::date + :dias_para_voltar
    WHERE b.situacao = 'resolvido' AND b.id_local IS NOT NULL
)
SELECT
    b.orgao,
    count(*) FILTER (WHERE b.situacao <> 'falhou')::int AS encaminhados,
    count(*) FILTER (WHERE b.situacao = 'falhou')::int AS falhas,
    count(*) FILTER (WHERE b.situacao = 'enviado')::int AS novas,
    count(*) FILTER (WHERE b.situacao = 'recebido')::int AS em_atendimento,
    count(*) FILTER (
        WHERE b.situacao IN ('enviado', 'recebido') AND b.prazo_de_resposta < :hoje
    )::int AS vencidas,
    count(*) FILTER (WHERE b.situacao = 'resolvido')::int AS resolvidas,
    count(*) FILTER (
        WHERE b.situacao = 'resolvido' AND b.resolvido_em::date <= b.prazo_de_resposta
    )::int AS resolvidas_no_prazo,
    count(*) FILTER (
        WHERE b.situacao = 'resolvido' AND b.resolvido_em::date > :desde_das_recentes
    )::int AS resolvidas_em_30_dias,
    count(*) FILTER (WHERE b.situacao = 'devolvido')::int AS devolvidas,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY b.resolvido_em::date - b.criado_em::date)
        FILTER (WHERE b.resolvido_em IS NOT NULL) AS mediana_de_dias_ate_resolver,
    count(v.id)::int AS voltaram_a_ser_pedidas
FROM base b
LEFT JOIN voltaram v ON v.id = b.id
GROUP BY b.orgao
"""
SEMANAS = f"""
WITH semanas AS (
    SELECT generate_series(
        date_trunc('week', CAST(:hoje AS date)) - make_interval(weeks => :semanas - 1),
        date_trunc('week', CAST(:hoje AS date)),
        interval '1 week'
    )::date AS inicio
),
recebidas AS (
    SELECT date_trunc('week', e.criado_em)::date AS inicio, count(*)::int AS quantidade
    FROM app.encaminhamento e
    WHERE e.situacao <> 'falhou' AND {DO_ORGAO}
    GROUP BY 1
),
resolvidas AS (
    SELECT date_trunc('week', ev.ocorrido_em)::date AS inicio, count(*)::int AS quantidade
    FROM app.evento_de_encaminhamento ev
    JOIN app.encaminhamento e ON e.id = ev.encaminhamento_id
    WHERE ev.situacao = 'resolvido' AND {DO_ORGAO}
    GROUP BY 1
)
SELECT s.inicio, coalesce(r.quantidade, 0), coalesce(z.quantidade, 0)
FROM semanas s
LEFT JOIN recebidas r ON r.inicio = s.inicio
LEFT JOIN resolvidas z ON z.inicio = s.inicio
ORDER BY s.inicio
"""
ABERTAS_POR_BAIRRO = """
SELECT bairro_oficial, count(*)::int
FROM app.encaminhamento
WHERE orgao = :orgao AND situacao IN ('enviado', 'recebido') AND bairro_oficial IS NOT NULL
GROUP BY bairro_oficial
"""
RESOLVIDAS_POR_TEMA = """
SELECT coalesce(categoria, :sem_tema), count(*)::int
FROM app.encaminhamento
WHERE orgao = :orgao AND situacao = 'resolvido'
GROUP BY 1
ORDER BY 2 DESC, 1
LIMIT :limite
"""
PESSOAS_COM_RETORNO = """
SELECT count(DISTINCT pessoas.usuario_id)::int
FROM app.encaminhamento e
JOIN LATERAL (
    SELECT p.usuario_id FROM app.pedido_acompanhado p
    WHERE e.protocolo_de_origem IS NOT NULL AND p.protocolo = e.protocolo_de_origem
    UNION
    SELECT c.usuario_id FROM app.contribuicao c
    WHERE e.contribuicao_id IS NOT NULL AND e.contribuicao_id IN (c.id, c.principal_id)
        AND c.usuario_id IS NOT NULL
) pessoas ON true
WHERE e.orgao = :orgao AND e.situacao = 'resolvido'
"""
OPCOES_DE_FILTRO = """
SELECT
    array_remove(array_agg(DISTINCT bairro_oficial ORDER BY bairro_oficial), NULL),
    array_remove(array_agg(DISTINCT categoria ORDER BY categoria), NULL)
FROM app.encaminhamento
WHERE orgao = :orgao AND situacao <> 'falhou'
"""


def _indicadores(linha: Row[Any]) -> IndicadoresDoOrgao:
    dados = dict(linha._mapping)
    mediana = dados.pop("mediana_de_dias_ate_resolver")
    return IndicadoresDoOrgao(
        orgao=Orgao(dados.pop("orgao")),
        mediana_de_dias_ate_resolver=float(mediana) if mediana is not None else None,
        **dados,
    )


class IndicadoresDoCicloSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def por_orgao(self, hoje: date, orgao: Orgao | None = None) -> list[IndicadoresDoOrgao]:
        parametros = {
            "orgao": orgao.value if orgao else None,
            "hoje": hoje,
            "desde_das_recentes": hoje - timedelta(days=DIAS_DAS_RESOLVIDAS_RECENTES),
            "dias_para_voltar": DIAS_PARA_VOLTAR_A_SER_PEDIDO,
        }
        return [_indicadores(linha) for linha in self._sessao.execute(text(POR_ORGAO), parametros)]

    def semanas(self, hoje: date, orgao: Orgao | None = None) -> list[SemanaDoCiclo]:
        parametros = {
            "orgao": orgao.value if orgao else None,
            "hoje": hoje,
            "semanas": SEMANAS_NA_SERIE,
        }
        return [SemanaDoCiclo(*linha) for linha in self._sessao.execute(text(SEMANAS), parametros)]

    def abertas_por_bairro(self, orgao: Orgao) -> dict[str, int]:
        linhas = self._sessao.execute(text(ABERTAS_POR_BAIRRO), {"orgao": orgao.value})
        return {bairro: quantidade for bairro, quantidade in linhas}

    def resolvidas_por_tema(self, orgao: Orgao) -> list[ContagemPorTema]:
        parametros = {
            "orgao": orgao.value,
            "sem_tema": SEM_TEMA,
            "limite": TEMAS_RESOLVIDOS_MOSTRADOS,
        }
        linhas = self._sessao.execute(text(RESOLVIDAS_POR_TEMA), parametros)
        return [ContagemPorTema(*linha) for linha in linhas]

    def pessoas_com_retorno(self, orgao: Orgao) -> int:
        parametros = {"orgao": orgao.value}
        return int(self._sessao.execute(text(PESSOAS_COM_RETORNO), parametros).scalar_one())

    def opcoes_de_filtro(self, orgao: Orgao) -> OpcoesDeFiltro:
        bairros, categorias = self._sessao.execute(
            text(OPCOES_DE_FILTRO), {"orgao": orgao.value}
        ).one()
        return OpcoesDeFiltro(list(bairros or []), list(categorias or []))
