from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil

LARGURA_PADRAO = 0.6


@dataclass(frozen=True)
class Ponto:
    x: float
    y: float


def _peso_tricubo(distancia: float, alcance: float) -> float:
    if alcance == 0:
        return 1.0
    proporcao = min(abs(distancia) / alcance, 1.0)
    return (1 - proporcao**3) ** 3


def _ajustar_localmente(pontos: Sequence[Ponto], alvo: float, vizinhos: int) -> float:
    proximos = sorted(pontos, key=lambda ponto: abs(ponto.x - alvo))[:vizinhos]
    alcance = max(abs(ponto.x - alvo) for ponto in proximos)
    pesos = [_peso_tricubo(ponto.x - alvo, alcance) for ponto in proximos]
    soma = sum(pesos)
    if soma == 0:
        return sum(ponto.y for ponto in proximos) / len(proximos)
    media_x = sum(p * ponto.x for p, ponto in zip(pesos, proximos, strict=True)) / soma
    media_y = sum(p * ponto.y for p, ponto in zip(pesos, proximos, strict=True)) / soma
    variacao = sum(p * (ponto.x - media_x) ** 2 for p, ponto in zip(pesos, proximos, strict=True))
    if variacao == 0:
        return media_y
    inclinacao = (
        sum(
            p * (ponto.x - media_x) * (ponto.y - media_y)
            for p, ponto in zip(pesos, proximos, strict=True)
        )
        / variacao
    )
    return media_y + inclinacao * (alvo - media_x)


def suavizar(pontos: Sequence[Ponto], largura: float = LARGURA_PADRAO) -> list[Ponto]:
    """Tendência suavizada (LOESS): regressão local, ponderada pela distância até cada x."""
    if len(pontos) < 3:
        return []
    vizinhos = max(ceil(largura * len(pontos)), 2)
    distintos = sorted({ponto.x for ponto in pontos})
    return [Ponto(x, _ajustar_localmente(pontos, x, vizinhos)) for x in distintos]
