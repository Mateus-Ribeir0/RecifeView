from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

from app.domain.suavizacao import Ponto

POPULACAO_MINIMA_PER_CAPITA = 1000
HABITANTES_DA_TAXA = 1000
QUANTIDADE_DE_FAIXAS = 5


@dataclass(frozen=True)
class FaixaDeTaxa:
    inicio: float
    fim: float


@dataclass(frozen=True)
class VolumeDoBairro:
    bairro_oficial: str
    n: int


@dataclass(frozen=True)
class IndicadorDeTerritorio:
    volume: int
    taxa: float | None
    classe: int | None


@dataclass(frozen=True)
class BairroDoTerritorio:
    bairro_oficial: str
    nome: str
    rpa: str
    populacao: int
    pct_favela: float
    taxa_confiavel: bool
    em_destaque: bool
    central_156: IndicadorDeTerritorio
    defesa_civil: IndicadorDeTerritorio
    pct_reincidencia_156: float | None
    pct_atraso_156: float | None
    abertos_156: int | None


@dataclass(frozen=True)
class Territorio:
    bairros: list[BairroDoTerritorio]
    faixas_156: list[FaixaDeTaxa]
    faixas_defesa_civil: list[FaixaDeTaxa]
    tendencia_156: list[Ponto]
    tendencia_defesa_civil: list[Ponto]
    anos_156: int
    anos_defesa_civil: int


def calcular_taxa(volume: int, anos: int, populacao: int) -> float:
    return volume / max(anos, 1) / populacao * HABITANTES_DA_TAXA


def _quantil_linear(ordenados: Sequence[float], posicao: float) -> float:
    indice = posicao * (len(ordenados) - 1)
    abaixo = int(indice)
    acima = min(abaixo + 1, len(ordenados) - 1)
    return ordenados[abaixo] + (ordenados[acima] - ordenados[abaixo]) * (indice - abaixo)


def limites_das_faixas(taxas: Sequence[float]) -> list[FaixaDeTaxa]:
    """Cinco faixas com o mesmo número de bairros; limites repetidos juntam faixas vizinhas."""
    ordenadas = sorted(taxas)
    if not ordenadas:
        return []
    cortes = [
        _quantil_linear(ordenadas, indice / QUANTIDADE_DE_FAIXAS)
        for indice in range(QUANTIDADE_DE_FAIXAS + 1)
    ]
    unicos = sorted(set(cortes))
    if len(unicos) < 2:
        return [FaixaDeTaxa(unicos[0], unicos[0])]
    return [FaixaDeTaxa(inicio, fim) for inicio, fim in pairwise(unicos)]


def classe_da_taxa(taxa: float | None, faixas: Sequence[FaixaDeTaxa]) -> int | None:
    if taxa is None or not faixas:
        return None
    for classe, faixa in enumerate(faixas, start=1):
        if taxa <= faixa.fim:
            return classe
    return len(faixas)
