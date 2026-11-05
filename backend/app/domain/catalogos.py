from dataclasses import dataclass


@dataclass(frozen=True)
class BairroDoCatalogo:
    bairro_oficial: str
    nome: str
    rpa: str
    populacao: int
    pct_favela: float
    taxa_confiavel: bool


@dataclass(frozen=True)
class FonteDoCatalogo:
    codigo: str
    rotulo: str
    registros: int


@dataclass(frozen=True)
class CatalogoDeFiltros:
    ano_minimo: int
    ano_maximo: int
    rpas: list[str]
    bairros: list[BairroDoCatalogo]
    categorias: list[str]
    fontes: list[FonteDoCatalogo]
