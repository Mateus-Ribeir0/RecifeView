from dataclasses import dataclass
from datetime import date, datetime

from app.domain.filtros import Filtros


@dataclass(frozen=True)
class Referencia:
    """O que diz de quando são os dados do painel."""

    data_referencia: date
    atualizado_em: datetime | None


@dataclass(frozen=True)
class Procedencia:
    fontes: tuple[str, ...]
    filtros: Filtros
    n: int
    atualizado_em: datetime | None
