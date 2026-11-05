from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.catalogos import BairroDoCatalogo, CatalogoDeFiltros, FonteDoCatalogo
from app.domain.fontes import ROTULOS_DAS_FONTES, Fonte
from app.domain.procedencia import Referencia
from app.domain.territorio import POPULACAO_MINIMA_PER_CAPITA

BAIRROS = """
SELECT bairro_oficial, nome, rpa, populacao, pct_favela, populacao >= :populacao_minima
FROM ouro.dim_bairro
ORDER BY nome
"""
CATEGORIAS_DO_156 = """
SELECT categoria
FROM ouro.mv_demanda
WHERE fonte = :fonte AND categoria IS NOT NULL
GROUP BY categoria
ORDER BY sum(n) DESC
"""
REGISTROS_POR_FONTE = "SELECT fonte, sum(n)::int FROM ouro.mv_demanda GROUP BY fonte"
ANOS = "SELECT coalesce(min(ano), 2012), coalesce(max(ano), 2026) FROM ouro.mv_demanda"
REFERENCIA = """
SELECT r.data_referencia, (
    SELECT max(concluida_em) FROM app.importacao WHERE status = 'CONCLUIDA'
)
FROM ouro.vw_referencia r
"""


class CatalogoRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def filtros(self) -> CatalogoDeFiltros:
        ano_minimo, ano_maximo = self._sessao.execute(text(ANOS)).one()
        parametros = {"populacao_minima": POPULACAO_MINIMA_PER_CAPITA}
        bairros = [
            BairroDoCatalogo(*linha) for linha in self._sessao.execute(text(BAIRROS), parametros)
        ]
        categorias = self._sessao.scalars(
            text(CATEGORIAS_DO_156), {"fonte": Fonte.CENTRAL_156.value}
        ).all()
        registros: dict[str, int] = {
            fonte: n for fonte, n in self._sessao.execute(text(REGISTROS_POR_FONTE))
        }
        fontes = [
            FonteDoCatalogo(fonte.value, rotulo, registros.get(fonte.value, 0))
            for fonte, rotulo in ROTULOS_DAS_FONTES.items()
        ]
        rpas = sorted({bairro.rpa for bairro in bairros})
        return CatalogoDeFiltros(ano_minimo, ano_maximo, rpas, bairros, list(categorias), fontes)


class ReferenciaRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def atual(self) -> Referencia:
        linha = self._sessao.execute(text(REFERENCIA)).one()
        return Referencia(linha[0], linha[1])
