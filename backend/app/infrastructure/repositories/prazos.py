from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.filtros import Filtros
from app.domain.prazos import (
    ABERTOS_MINIMOS_POR_CATEGORIA,
    CATEGORIAS_NO_ESTOQUE,
    DIAS_DE_CAUDA_LONGA,
    FAIXAS_DE_PRAZO,
    EstoqueAberto,
    EstoquePorCategoria,
    FaixaDePrazo,
    PrazoPorAno,
    PrazoPorCategoria,
    ResumoDosPrazos,
)
from app.infrastructure.repositories.recorte import (
    SEM_MESMO_DIA,
    Recorte,
    por_categoria,
    por_territorio,
    recorte_completo,
)


def _recorte(filtros: Filtros, sem_mesmo_dia: bool) -> Recorte:
    recorte = recorte_completo(filtros)
    return recorte.com_condicao(SEM_MESMO_DIA) if sem_mesmo_dia else recorte


def _sql_de_percentis_por_grupo(coluna: str, recorte: Recorte) -> str:
    return f"""
    WITH valores AS (
        SELECT {coluna} AS grupo, dias, sum(n) AS n
        FROM ouro.mv_prazos_156 {recorte.onde}
        GROUP BY 1, 2
    ),
    acumulado AS (
        SELECT
            grupo, dias, n,
            sum(n) OVER (PARTITION BY grupo ORDER BY dias) AS soma,
            sum(n) OVER (PARTITION BY grupo) AS total
        FROM valores
    )
    SELECT
        grupo,
        max(total)::int AS pedidos,
        min(dias) FILTER (WHERE soma >= 0.5 * total) AS mediana,
        min(dias) FILTER (WHERE soma >= 0.9 * total) AS p90,
        coalesce(sum(n) FILTER (WHERE dias = 0), 0)::float / max(total) * 100 AS pct_mesmo_dia
    FROM acumulado
    GROUP BY grupo
    """


def _rotulo_da_faixa(dias: int) -> str:
    for fim, rotulo in FAIXAS_DE_PRAZO:
        if fim is None or dias <= fim:
            return rotulo
    return FAIXAS_DE_PRAZO[-1][1]


def _sql_das_situacoes_abertas(recorte: Recorte) -> str:
    aberto = recorte.com_condicao("t.data_fim IS NULL")
    return f"""
    SELECT
        t.categoria,
        count(*)::int AS abertos,
        (count(*) FILTER (
            WHERE r.data_referencia - t.data_abertura > t.prazo_tipico_dias
        ))::int AS acima_do_prazo
    FROM ouro.mv_linha_do_tempo_156 t
    CROSS JOIN ouro.vw_referencia r
    {aberto.onde}
    GROUP BY t.categoria
    """


class PrazoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def resumo(self, filtros: Filtros, sem_mesmo_dia: bool) -> ResumoDosPrazos:
        recorte = _recorte(filtros, sem_mesmo_dia)
        consulta = f"""
        WITH valores AS (
            SELECT dias, sum(n) AS n FROM ouro.mv_prazos_156 {recorte.onde} GROUP BY dias
        ),
        acumulado AS (
            SELECT dias, n, sum(n) OVER (ORDER BY dias) AS soma, sum(n) OVER () AS total
            FROM valores
        )
        SELECT
            coalesce(max(total), 0)::int,
            min(dias) FILTER (WHERE soma >= 0.5 * total),
            min(dias) FILTER (WHERE soma >= 0.9 * total),
            coalesce(sum(n) FILTER (WHERE dias = 0), 0)::float / nullif(max(total), 0) * 100,
            coalesce(sum(n) FILTER (WHERE dias > :cauda), 0)::float / nullif(max(total), 0) * 100
        FROM acumulado
        """
        parametros = {**recorte.parametros, "cauda": DIAS_DE_CAUDA_LONGA}
        return ResumoDosPrazos(*self._sessao.execute(text(consulta), parametros).one())

    def por_ano(self, filtros: Filtros, sem_mesmo_dia: bool) -> list[PrazoPorAno]:
        recorte = _recorte(filtros, sem_mesmo_dia)
        consulta = _sql_de_percentis_por_grupo("ano", recorte) + " ORDER BY grupo"
        linhas = self._sessao.execute(text(consulta), recorte.parametros)
        return [PrazoPorAno(ano, mediana, p90) for ano, _, mediana, p90, _ in linhas]

    def faixas(self, filtros: Filtros, sem_mesmo_dia: bool) -> list[FaixaDePrazo]:
        recorte = _recorte(filtros, sem_mesmo_dia)
        consulta = f"SELECT dias, sum(n)::int FROM ouro.mv_prazos_156 {recorte.onde} GROUP BY dias"
        contagem = {rotulo: 0 for _, rotulo in FAIXAS_DE_PRAZO}
        for dias, n in self._sessao.execute(text(consulta), recorte.parametros):
            contagem[_rotulo_da_faixa(dias)] += n
        total = sum(contagem.values())
        return [
            FaixaDePrazo(rotulo, n, n / total * 100 if total else 0.0)
            for rotulo, n in contagem.items()
        ]

    def por_categoria(self, filtros: Filtros, sem_mesmo_dia: bool) -> list[PrazoPorCategoria]:
        recorte = _recorte(filtros, sem_mesmo_dia)
        consulta = _sql_de_percentis_por_grupo("categoria", recorte)
        linhas = self._sessao.execute(text(consulta), recorte.parametros)
        return [PrazoPorCategoria(*linha) for linha in linhas if linha[0] is not None]

    def estoque(self, filtros: Filtros) -> EstoqueAberto:
        recorte = por_territorio(filtros).com(por_categoria(filtros))
        linhas = self._sessao.execute(text(_sql_das_situacoes_abertas(recorte)), recorte.parametros)
        categorias = [EstoquePorCategoria(*linha) for linha in linhas if linha[0] is not None]
        abertos = sum(item.abertos for item in categorias)
        acima = sum(item.acima_do_prazo for item in categorias)
        relevantes = [item for item in categorias if item.abertos >= ABERTOS_MINIMOS_POR_CATEGORIA]
        maiores = sorted(relevantes, key=lambda item: item.acima_do_prazo, reverse=True)
        return EstoqueAberto(
            abertos,
            acima,
            acima / abertos * 100 if abertos else None,
            maiores[:CATEGORIAS_NO_ESTOQUE],
        )
