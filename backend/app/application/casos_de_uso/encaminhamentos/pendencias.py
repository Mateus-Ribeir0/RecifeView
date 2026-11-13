from dataclasses import dataclass
from typing import Protocol

from app.application.portas.encaminhamentos import (
    EncaminhamentoRepository,
    PendenciasDosEncaminhamentos,
)
from app.application.portas.relogio import Relogio


class DuplasDoPenteFino(Protocol):
    def contar_pares_abertos(self) -> int: ...


@dataclass(frozen=True)
class PendenciasDoPainel:
    encaminhamentos: PendenciasDosEncaminhamentos
    duplas_no_pente_fino: int


@dataclass(frozen=True)
class ConsultarPendenciasDoPainel:
    """O que espera um passo da gestão, para os contadores do menu."""

    encaminhamentos: EncaminhamentoRepository
    contribuicoes: DuplasDoPenteFino
    relogio: Relogio

    def executar(self) -> PendenciasDoPainel:
        hoje = self.relogio.agora().date()
        return PendenciasDoPainel(
            self.encaminhamentos.contar_pendencias(hoje),
            self.contribuicoes.contar_pares_abertos(),
        )
