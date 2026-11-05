from dataclasses import dataclass


@dataclass(frozen=True)
class DemandaPorAno:
    ano: int
    fonte: str
    n: int


@dataclass(frozen=True)
class ResumoDasIndicacoes:
    total: int
    enviadas: int
    respondidas: int
    mediana_dias_ate_envio: float | None
    mediana_dias_ate_resposta: float | None

    @property
    def pct_enviadas(self) -> float | None:
        return self.enviadas / self.total * 100 if self.total else None

    @property
    def pct_respondidas(self) -> float | None:
        return self.respondidas / self.total * 100 if self.total else None


@dataclass(frozen=True)
class PercentisDePrazo:
    mediana: int | None
    p90: int | None


@dataclass(frozen=True)
class VisaoGeral:
    demandas: int
    indicacoes: ResumoDasIndicacoes
    pct_local_repetido: float | None
    prazo: PercentisDePrazo
    serie: list[DemandaPorAno]
