from dataclasses import dataclass
from datetime import date

from app.domain.encaminhamento.orgaos import Orgao

PERCENTUAL = 100
DIAS_PARA_VOLTAR_A_SER_PEDIDO = 30
SEMANAS_NA_SERIE = 12


@dataclass(frozen=True)
class IndicadoresDoOrgao:
    """O ciclo de um órgão, contado sobre todos os encaminhamentos que ele recebeu."""

    orgao: Orgao
    encaminhados: int = 0
    falhas: int = 0
    novas: int = 0
    em_atendimento: int = 0
    vencidas: int = 0
    resolvidas: int = 0
    resolvidas_no_prazo: int = 0
    resolvidas_em_30_dias: int = 0
    devolvidas: int = 0
    mediana_de_dias_ate_resolver: float | None = None
    voltaram_a_ser_pedidas: int = 0

    @property
    def abertas(self) -> int:
        return self.novas + self.em_atendimento

    @property
    def pct_no_prazo(self) -> float | None:
        if not self.resolvidas:
            return None
        return PERCENTUAL * self.resolvidas_no_prazo / self.resolvidas


@dataclass(frozen=True)
class SemanaDoCiclo:
    inicio: date
    recebidas: int = 0
    resolvidas: int = 0


@dataclass(frozen=True)
class ContagemPorTema:
    categoria: str
    quantidade: int
