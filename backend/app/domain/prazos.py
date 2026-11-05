from dataclasses import dataclass

CATEGORIA_MINIMA_COM_MUITOS_PEDIDOS = 1000
CATEGORIA_MINIMA_COM_POUCOS_PEDIDOS = 30
LIMITE_DE_MUITOS_PEDIDOS = 200_000
ABERTOS_MINIMOS_POR_CATEGORIA = 20
CATEGORIAS_NO_ESTOQUE = 12
DIAS_DE_CAUDA_LONGA = 90

# Fim de cada faixa em dias, com o rótulo. A última não tem fim.
FAIXAS_DE_PRAZO: tuple[tuple[int | None, str], ...] = (
    (0, "mesmo dia"),
    (7, "1 a 7 dias"),
    (30, "8 a 30 dias"),
    (90, "31 a 90 dias"),
    (365, "91 a 365 dias"),
    (None, "mais de 1 ano"),
)


def minimo_de_pedidos_por_categoria(total: int) -> int:
    if total > LIMITE_DE_MUITOS_PEDIDOS:
        return CATEGORIA_MINIMA_COM_MUITOS_PEDIDOS
    return CATEGORIA_MINIMA_COM_POUCOS_PEDIDOS


@dataclass(frozen=True)
class ResumoDosPrazos:
    pedidos: int
    mediana: int | None
    p90: int | None
    pct_mesmo_dia: float | None
    pct_acima_de_90_dias: float | None


@dataclass(frozen=True)
class PrazoPorAno:
    ano: int
    mediana: int
    p90: int


@dataclass(frozen=True)
class FaixaDePrazo:
    faixa: str
    n: int
    pct: float


@dataclass(frozen=True)
class PrazoPorCategoria:
    categoria: str
    pedidos: int
    mediana: int
    p90: int
    pct_mesmo_dia: float


@dataclass(frozen=True)
class EstoquePorCategoria:
    categoria: str
    abertos: int
    acima_do_prazo: int


@dataclass(frozen=True)
class EstoqueAberto:
    abertos: int
    acima_do_prazo: int
    pct_acima_do_prazo: float | None
    por_categoria: list[EstoquePorCategoria]


@dataclass(frozen=True)
class Prazos:
    resumo: ResumoDosPrazos
    por_ano: list[PrazoPorAno]
    faixas: list[FaixaDePrazo]
    minimo_por_categoria: int
    por_categoria: list[PrazoPorCategoria]
    estoque: EstoqueAberto
