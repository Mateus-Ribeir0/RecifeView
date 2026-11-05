from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.visao_geral import DemandaPorAno, PercentisDePrazo, ResumoDasIndicacoes
from app.infrastructure.repositories.recorte import (
    Recorte,
    por_ano,
    por_categoria,
    por_territorio,
    recorte_completo,
)

SO_DEMANDA_DO_CIDADAO = "NOT (fonte = 'DEFESA_CIVIL' AND iniciativa IS DISTINCT FROM 'CIDADAO')"
FONTES_COM_CATEGORIA_DE_SERVICO = (Fonte.CENTRAL_156.value, Fonte.CAMARA.value)


def _recorte_da_demanda(filtros: Filtros) -> Recorte:
    recorte = por_ano(filtros).com(por_territorio(filtros)).com_condicao(SO_DEMANDA_DO_CIDADAO)
    if not filtros.categorias:
        return recorte
    fontes = Recorte(
        ("fonte = ANY(:fontes_com_categoria)",),
        {"fontes_com_categoria": list(FONTES_COM_CATEGORIA_DE_SERVICO)},
    )
    return recorte.com(fontes, por_categoria(filtros))


def sql_de_percentis(tabela: str, recorte: Recorte) -> str:
    return f"""
    WITH valores AS (
        SELECT dias, sum(n) AS n FROM {tabela} {recorte.onde} GROUP BY dias
    ),
    acumulado AS (
        SELECT dias, sum(n) OVER (ORDER BY dias) AS soma, sum(n) OVER () AS total FROM valores
    )
    SELECT
        min(dias) FILTER (WHERE soma >= 0.5 * total),
        min(dias) FILTER (WHERE soma >= 0.9 * total)
    FROM acumulado
    """


class VisaoGeralRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def demandas_por_ano(self, filtros: Filtros) -> list[DemandaPorAno]:
        recorte = _recorte_da_demanda(filtros)
        consulta = f"""
        SELECT ano, fonte, sum(n)::int FROM ouro.mv_demanda {recorte.onde}
        GROUP BY ano, fonte ORDER BY ano, fonte
        """
        linhas = self._sessao.execute(text(consulta), recorte.parametros)
        return [DemandaPorAno(*linha) for linha in linhas]

    def resumo_das_indicacoes(self, filtros: Filtros) -> ResumoDasIndicacoes:
        recorte = recorte_completo(filtros)
        consulta = f"""
        SELECT
            count(*),
            count(*) FILTER (WHERE enviada),
            count(*) FILTER (WHERE respondida),
            percentile_cont(0.5) WITHIN GROUP (ORDER BY dias_ate_envio),
            percentile_cont(0.5) WITHIN GROUP (ORDER BY dias_ate_resposta)
        FROM ouro.mv_camara_indicacoes {recorte.onde}
        """
        return ResumoDasIndicacoes(*self._sessao.execute(text(consulta), recorte.parametros).one())

    def pct_local_repetido(self, filtros: Filtros) -> float | None:
        recorte = recorte_completo(filtros)
        consulta = f"""
        SELECT sum(repetidos)::float / nullif(sum(registros), 0) * 100
        FROM ouro.mv_reincidencia_156 {recorte.onde}
        """
        pct: float | None = self._sessao.scalar(text(consulta), recorte.parametros)
        return pct

    def percentis_de_prazo(self, filtros: Filtros) -> PercentisDePrazo:
        recorte = recorte_completo(filtros)
        consulta = sql_de_percentis("ouro.mv_prazos_156", recorte)
        return PercentisDePrazo(*self._sessao.execute(text(consulta), recorte.parametros).one())
