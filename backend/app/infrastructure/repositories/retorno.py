from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.filtros import Filtros
from app.domain.retorno import (
    CANAIS_PRINCIPAIS_DA_OUVIDORIA,
    CANAL_AGRUPADO,
    CANAL_DO_APP,
    CATEGORIAS_NO_MAPA_DE_CALOR,
    DESFECHO_PADRAO,
    DESFECHOS,
    ORGAO_AGRUPADO,
    ORGAOS_NO_MAPA_DE_CALOR,
    ORGAOS_NO_SANKEY,
    CaminhoDaCategoria,
    CanaisDaOuvidoria,
    CanalPorAno,
    CelulaDeDestino,
    DispersaoDaCategoria,
    FluxoDeOrgao,
    RespostaPorAno,
)
from app.infrastructure.repositories.recorte import Recorte, por_ano, recorte_completo


def _sql_das_celulas(recorte: Recorte) -> str:
    return f"""
    WITH base AS (
        SELECT categoria, orgao FROM ouro.mv_camara_indicacoes
        {recorte.com_condicao("categoria IS NOT NULL AND orgao IS NOT NULL").onde}
    ),
    categorias AS (
        SELECT categoria FROM base GROUP BY categoria
        ORDER BY count(*) DESC, categoria LIMIT :categorias_no_mapa
    ),
    orgaos AS (
        SELECT orgao FROM base GROUP BY orgao ORDER BY count(*) DESC, orgao LIMIT :orgaos_no_mapa
    ),
    agrupado AS (
        SELECT
            b.categoria,
            CASE WHEN b.orgao IN (SELECT orgao FROM orgaos) THEN b.orgao ELSE :agrupado END AS orgao
        FROM base b
        WHERE b.categoria IN (SELECT categoria FROM categorias)
    ),
    contagem AS (SELECT categoria, orgao, count(*) AS n FROM agrupado GROUP BY 1, 2)
    SELECT
        categoria, orgao, n::int,
        n::float / sum(n) OVER (PARTITION BY categoria) * 100
    FROM contagem
    """


def _parametros_do_mapa(recorte: Recorte) -> dict[str, object]:
    return {
        **recorte.parametros,
        "categorias_no_mapa": CATEGORIAS_NO_MAPA_DE_CALOR,
        "orgaos_no_mapa": ORGAOS_NO_MAPA_DE_CALOR,
        "agrupado": ORGAO_AGRUPADO,
    }


class RetornoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def resposta_por_ano(self, filtros: Filtros) -> list[RespostaPorAno]:
        recorte = recorte_completo(filtros)
        consulta = f"""
        SELECT
            ano, count(*)::int, (count(*) FILTER (WHERE respondida))::int,
            mode() WITHIN GROUP (ORDER BY canal_envio),
            (count(*) FILTER (WHERE respondida))::float / count(*) * 100
        FROM ouro.mv_camara_indicacoes {recorte.onde}
        GROUP BY ano ORDER BY ano
        """
        linhas = self._sessao.execute(text(consulta), recorte.parametros)
        return [RespostaPorAno(*linha) for linha in linhas]

    def celulas_de_destino(self, filtros: Filtros) -> list[CelulaDeDestino]:
        recorte = recorte_completo(filtros)
        linhas = self._sessao.execute(text(_sql_das_celulas(recorte)), _parametros_do_mapa(recorte))
        return [CelulaDeDestino(*linha) for linha in linhas]

    def dispersoes(self, filtros: Filtros) -> list[DispersaoDaCategoria]:
        destinos = self._orgaos_por_categoria(recorte_completo(filtros))
        return _dispersoes_das_celulas(self.celulas_de_destino(filtros), destinos)

    def _orgaos_por_categoria(self, recorte: Recorte) -> dict[str, int]:
        filtrado = recorte.com_condicao("categoria IS NOT NULL AND orgao IS NOT NULL")
        consulta = f"""
        SELECT categoria, count(DISTINCT orgao)::int
        FROM ouro.mv_camara_indicacoes {filtrado.onde}
        GROUP BY categoria
        """
        linhas = self._sessao.execute(text(consulta), filtrado.parametros)
        return {categoria: orgaos for categoria, orgaos in linhas}

    def caminho_da_categoria(self, filtros: Filtros, categoria: str) -> CaminhoDaCategoria:
        recorte = recorte_completo(filtros).com(
            Recorte(
                ("categoria = :foco", "orgao IS NOT NULL"),
                {"foco": categoria},
            )
        )
        consulta = f"""
        WITH base AS (
            SELECT orgao, desfecho FROM ouro.mv_camara_indicacoes {recorte.onde}
        ),
        orgaos AS (
            SELECT orgao FROM base GROUP BY orgao
            ORDER BY count(*) DESC, orgao LIMIT :orgaos_no_sankey
        )
        SELECT
            CASE WHEN orgao IN (SELECT orgao FROM orgaos) THEN orgao ELSE :agrupado END,
            desfecho, count(*)::int
        FROM base
        GROUP BY 1, 2
        """
        parametros = {
            **recorte.parametros,
            "orgaos_no_sankey": ORGAOS_NO_SANKEY,
            "agrupado": ORGAO_AGRUPADO,
        }
        fluxos: dict[tuple[str, str], int] = {}
        for orgao, desfecho, n in self._sessao.execute(text(consulta), parametros):
            chave = (orgao, DESFECHOS.get(desfecho, DESFECHO_PADRAO))
            fluxos[chave] = fluxos.get(chave, 0) + n
        return CaminhoDaCategoria(
            categoria, [FluxoDeOrgao(orgao, fim, n) for (orgao, fim), n in fluxos.items()]
        )

    def canais_da_ouvidoria(self, filtros: Filtros) -> CanaisDaOuvidoria:
        recorte = por_ano(filtros)
        canais = self._canais_por_ano(recorte)
        total, no_prazo = self._sessao.execute(
            text(
                f"""
                SELECT sum(n)::int, sum(n) FILTER (WHERE no_prazo)::int
                FROM ouro.mv_ouvidoria {recorte.onde}
                """
            ),
            recorte.parametros,
        ).one()
        do_app = [canal for canal in canais if canal.canal == CANAL_DO_APP]
        ultimo = max(do_app, key=lambda canal: canal.ano) if do_app else None
        return CanaisDaOuvidoria(
            canais=canais,
            ano_do_app=ultimo.ano if ultimo else None,
            pct_do_app=ultimo.pct if ultimo else None,
            pct_no_prazo=(no_prazo or 0) / total * 100 if total else None,
            total=total or 0,
        )

    def _canais_por_ano(self, recorte: Recorte) -> list[CanalPorAno]:
        filtrado = recorte.com_condicao("canal_entrada IS NOT NULL")
        consulta = f"""
        WITH canais AS (
            SELECT
                ano,
                CASE WHEN canal_entrada = ANY(:principais) THEN canal_entrada ELSE :agrupado END
                    AS canal,
                sum(n) AS n
            FROM ouro.mv_ouvidoria {filtrado.onde}
            GROUP BY 1, 2
        )
        SELECT ano, canal, n::int, n::float / sum(n) OVER (PARTITION BY ano) * 100
        FROM canais ORDER BY ano, canal
        """
        parametros = {
            **filtrado.parametros,
            "principais": list(CANAIS_PRINCIPAIS_DA_OUVIDORIA),
            "agrupado": CANAL_AGRUPADO,
        }
        return [CanalPorAno(*linha) for linha in self._sessao.execute(text(consulta), parametros)]


def _dispersoes_das_celulas(
    celulas: list[CelulaDeDestino], orgaos_por_categoria: dict[str, int]
) -> list[DispersaoDaCategoria]:
    principais: dict[str, CelulaDeDestino] = {}
    for celula in celulas:
        atual = principais.get(celula.categoria)
        if atual is None or celula.pct > atual.pct:
            principais[celula.categoria] = celula
    dispersoes = [
        DispersaoDaCategoria(
            categoria, celula.orgao, celula.pct, orgaos_por_categoria.get(categoria, 0)
        )
        for categoria, celula in principais.items()
    ]
    return sorted(dispersoes, key=lambda dispersao: dispersao.pct_principal)
