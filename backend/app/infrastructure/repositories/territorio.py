from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.catalogos import BairroDoCatalogo
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte, Iniciativa
from app.domain.territorio import POPULACAO_MINIMA_PER_CAPITA, VolumeDoBairro
from app.infrastructure.repositories.recorte import Recorte, por_ano, por_categoria

BAIRROS = """
SELECT bairro_oficial, nome, rpa, populacao, pct_favela, populacao >= :populacao_minima
FROM ouro.dim_bairro
ORDER BY nome
"""
INDICADORES = """
SELECT bairro_oficial, pct_reincidencia_156, pct_atraso_156, abertos_156
FROM ouro.mv_indicadores_bairro
"""


class TerritorioRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def _volumes(self, recorte: Recorte) -> tuple[list[VolumeDoBairro], int]:
        anos = self._sessao.scalar(
            text(f"SELECT count(DISTINCT ano) FROM ouro.mv_demanda {recorte.onde}"),
            recorte.parametros,
        )
        filtrado = recorte.com_condicao("bairro_oficial IS NOT NULL")
        consulta = f"""
        SELECT bairro_oficial, sum(n)::int FROM ouro.mv_demanda {filtrado.onde}
        GROUP BY bairro_oficial
        """
        linhas = self._sessao.execute(text(consulta), filtrado.parametros)
        return [VolumeDoBairro(*linha) for linha in linhas], anos or 0

    def volumes_de_156(self, filtros: Filtros) -> tuple[list[VolumeDoBairro], int]:
        fonte = Recorte(("fonte = :fonte",), {"fonte": Fonte.CENTRAL_156.value})
        return self._volumes(por_ano(filtros).com(fonte, por_categoria(filtros)))

    def volumes_da_defesa_civil(self, filtros: Filtros) -> tuple[list[VolumeDoBairro], int]:
        fonte = Recorte(
            ("fonte = :fonte", "iniciativa = :iniciativa"),
            {"fonte": Fonte.DEFESA_CIVIL.value, "iniciativa": Iniciativa.CIDADAO.value},
        )
        return self._volumes(por_ano(filtros).com(fonte))

    def bairros(self) -> list[BairroDoCatalogo]:
        parametros = {"populacao_minima": POPULACAO_MINIMA_PER_CAPITA}
        return [
            BairroDoCatalogo(*linha) for linha in self._sessao.execute(text(BAIRROS), parametros)
        ]

    def indicadores(self) -> dict[str, tuple[float | None, float | None, int]]:
        linhas = self._sessao.execute(text(INDICADORES))
        return {
            bairro: (reincidencia, atraso, abertos)
            for bairro, reincidencia, atraso, abertos in linhas
        }
