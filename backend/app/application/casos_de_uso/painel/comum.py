from dataclasses import dataclass

from app.application.portas.painel import CatalogoRepository
from app.domain.catalogos import CatalogoDeFiltros
from app.domain.fontes import Fonte
from app.domain.procedencia import Procedencia

TODAS_AS_FONTES = tuple(fonte.value for fonte in Fonte)


@dataclass(frozen=True)
class ResultadoDaConsulta[T]:
    dados: T
    meta: Procedencia


@dataclass(frozen=True)
class ListarFiltros:
    catalogo: CatalogoRepository

    def executar(self) -> CatalogoDeFiltros:
        return self.catalogo.filtros()
