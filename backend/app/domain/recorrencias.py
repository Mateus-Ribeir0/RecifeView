from dataclasses import dataclass

CATEGORIA_MINIMA_COM_MUITOS_PEDIDOS = 2000
CATEGORIA_MINIMA_COM_POUCOS_PEDIDOS = 50
LIMITE_DE_MUITOS_PEDIDOS = 100_000
PEDIDOS_DE_UM_PONTO_CRONICO = 10
PONTOS_CRONICOS_LISTADOS = 50


def minimo_de_pedidos_por_categoria(total: int) -> int:
    if total > LIMITE_DE_MUITOS_PEDIDOS:
        return CATEGORIA_MINIMA_COM_MUITOS_PEDIDOS
    return CATEGORIA_MINIMA_COM_POUCOS_PEDIDOS


@dataclass(frozen=True)
class IntervalosDeRepeticao:
    duplicidade: int
    intermediario: int
    reincidencia: int

    @property
    def total(self) -> int:
        return self.duplicidade + self.intermediario + self.reincidencia


@dataclass(frozen=True)
class RecorrenciaPorCategoria:
    categoria: str
    pedidos: int
    repetidos: int
    pct_repetidos: float
    intervalos: IntervalosDeRepeticao


@dataclass(frozen=True)
class PontoCronico:
    bairro_oficial: str | None
    categoria: str | None
    servico: str | None
    pedidos: int
    dias_distintos: int
    primeiro_ano: int
    ultimo_ano: int


@dataclass(frozen=True)
class Recorrencias:
    pedidos: int
    repetidos: int
    pct_repetidos: float | None
    intervalos: IntervalosDeRepeticao
    pontos_cronicos: int
    minimo_por_categoria: int
    por_categoria: list[RecorrenciaPorCategoria]
    lista_de_pontos: list[PontoCronico]
