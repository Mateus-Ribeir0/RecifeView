from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from app.domain.demanda_do_orgao import DemandaDoOrgao, PeriodoEmAnos
from app.domain.encaminhamento.desempenho import (
    ContagemPorTema,
    IndicadoresDoOrgao,
    SemanaDoCiclo,
)
from app.domain.encaminhamento.orgaos import Orgao


@dataclass(frozen=True)
class OpcoesDeFiltro:
    bairros: list[str] = field(default_factory=list)
    categorias: list[str] = field(default_factory=list)


class IndicadoresDoCicloRepository(Protocol):
    def por_orgao(self, hoje: date, orgao: Orgao | None = None) -> list[IndicadoresDoOrgao]: ...

    def semanas(self, hoje: date, orgao: Orgao | None = None) -> list[SemanaDoCiclo]: ...

    def abertas_por_bairro(self, orgao: Orgao) -> dict[str, int]: ...

    def resolvidas_por_tema(self, orgao: Orgao) -> list[ContagemPorTema]: ...

    def pessoas_com_retorno(self, orgao: Orgao) -> int: ...

    def opcoes_de_filtro(self, orgao: Orgao) -> OpcoesDeFiltro: ...


class DemandaDoOrgaoRepository(Protocol):
    def resumir(self, nomes_na_fonte: Sequence[str], periodo: PeriodoEmAnos) -> DemandaDoOrgao: ...
