from dataclasses import dataclass

from app.domain.erros import PeriodoInvalido

ANO_INICIAL_PADRAO = 2021
ANO_FINAL_PADRAO = 2025


@dataclass(frozen=True)
class Filtros:
    ano_inicio: int = ANO_INICIAL_PADRAO
    ano_fim: int = ANO_FINAL_PADRAO
    rpas: tuple[str, ...] = ()
    bairros: tuple[str, ...] = ()
    categorias: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.ano_inicio > self.ano_fim:
            raise PeriodoInvalido

    @property
    def tem_territorio(self) -> bool:
        return bool(self.rpas or self.bairros)
