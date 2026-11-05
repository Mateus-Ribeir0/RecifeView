from dataclasses import dataclass
from datetime import datetime

ANO_INICIAL_DA_COBERTURA = 2012


@dataclass(frozen=True)
class CoberturaPorFonte:
    fonte: str
    ano: int
    n: int


@dataclass(frozen=True)
class CorrecaoAplicada:
    correcao: str
    registros: int


@dataclass(frozen=True)
class SobreOsDados:
    cobertura: list[CoberturaPorFonte]
    correcoes: list[CorrecaoAplicada]
    registros_na_base: int
    atualizado_em: datetime | None
