from dataclasses import dataclass

from app.application.portas.painel import ReferenciaRepository, SobreRepository
from app.domain.sobre import SobreOsDados


@dataclass(frozen=True)
class ConsultarSobreOsDados:
    sobre: SobreRepository
    referencia: ReferenciaRepository

    def executar(self) -> SobreOsDados:
        return SobreOsDados(
            cobertura=self.sobre.cobertura(),
            correcoes=self.sobre.correcoes(),
            registros_na_base=self.sobre.registros_na_base(),
            atualizado_em=self.referencia.atual().atualizado_em,
        )
