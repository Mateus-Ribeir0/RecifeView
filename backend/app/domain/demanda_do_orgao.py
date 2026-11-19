from dataclasses import dataclass, field

TEMAS_MOSTRADOS = 10
SITUACOES_MOSTRADAS = 6


@dataclass(frozen=True)
class PeriodoEmAnos:
    ano_inicio: int
    ano_fim: int


@dataclass(frozen=True)
class DemandaPorAno:
    ano: int
    fonte: str
    quantidade: int


@dataclass(frozen=True)
class DemandaPorRotulo:
    rotulo: str
    quantidade: int


@dataclass(frozen=True)
class DemandaDoOrgao:
    """O que a base aberta registra com o nome do órgão: só contagens, nunca o texto dos pedidos."""

    total: int = 0
    sem_bairro: int = 0
    por_ano: list[DemandaPorAno] = field(default_factory=list)
    por_bairro: dict[str, int] = field(default_factory=dict)
    por_tema: list[DemandaPorRotulo] = field(default_factory=list)
    por_situacao: list[DemandaPorRotulo] = field(default_factory=list)
