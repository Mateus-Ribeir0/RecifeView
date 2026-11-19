from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.demanda_do_orgao import (
    SITUACOES_MOSTRADAS,
    TEMAS_MOSTRADOS,
    DemandaDoOrgao,
    DemandaPorAno,
    DemandaPorRotulo,
    PeriodoEmAnos,
)

DO_ORGAO = "orgao_na_fonte = ANY(:nomes) AND ano BETWEEN :ano_inicio AND :ano_fim"
NAO_INFORMADO = "NÃO INFORMADO"

POR_ANO = f"""
SELECT ano, fonte, sum(n)::int FROM ouro.mv_demanda_por_orgao
WHERE {DO_ORGAO}
GROUP BY ano, fonte
ORDER BY ano, fonte
"""
POR_BAIRRO = f"""
SELECT bairro_oficial, sum(n)::int FROM ouro.mv_demanda_por_orgao
WHERE {DO_ORGAO}
GROUP BY bairro_oficial
"""
POR_TEMA = f"""
SELECT coalesce(categoria, :nao_informado), sum(n)::int FROM ouro.mv_demanda_por_orgao
WHERE {DO_ORGAO}
GROUP BY 1
ORDER BY 2 DESC, 1
LIMIT :limite
"""
POR_SITUACAO = f"""
SELECT coalesce(situacao, :nao_informado), sum(n)::int FROM ouro.mv_demanda_por_orgao
WHERE {DO_ORGAO}
GROUP BY 1
ORDER BY 2 DESC, 1
LIMIT :limite
"""


class DemandaDoOrgaoSql:
    """Lê a view por órgão: a tabela fato tem 2,6 milhões de linhas e não é varrida na consulta."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def resumir(self, nomes_na_fonte: Sequence[str], periodo: PeriodoEmAnos) -> DemandaDoOrgao:
        if not nomes_na_fonte:
            return DemandaDoOrgao()
        filtro = {
            "nomes": list(nomes_na_fonte),
            "ano_inicio": periodo.ano_inicio,
            "ano_fim": periodo.ano_fim,
            "nao_informado": NAO_INFORMADO,
        }
        por_ano = [DemandaPorAno(*linha) for linha in self._sessao.execute(text(POR_ANO), filtro)]
        contagens: dict[str | None, int] = {
            bairro: quantidade
            for bairro, quantidade in self._sessao.execute(text(POR_BAIRRO), filtro)
        }
        sem_bairro = contagens.pop(None, 0)
        por_bairro = {bairro: n for bairro, n in contagens.items() if bairro is not None}
        return DemandaDoOrgao(
            total=sum(item.quantidade for item in por_ano),
            sem_bairro=sem_bairro,
            por_ano=por_ano,
            por_bairro=por_bairro,
            por_tema=self._rotulos(POR_TEMA, filtro, TEMAS_MOSTRADOS),
            por_situacao=self._rotulos(POR_SITUACAO, filtro, SITUACOES_MOSTRADAS),
        )

    def _rotulos(
        self, consulta: str, filtro: dict[str, object], limite: int
    ) -> list[DemandaPorRotulo]:
        linhas = self._sessao.execute(text(consulta), {**filtro, "limite": limite})
        return [DemandaPorRotulo(*linha) for linha in linhas]
