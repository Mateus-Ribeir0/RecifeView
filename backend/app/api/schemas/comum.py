from datetime import datetime

from pydantic import BaseModel

from app.domain.procedencia import Procedencia


class PeriodoResposta(BaseModel):
    inicio: int
    fim: int


class FiltrosAplicadosResposta(BaseModel):
    rpa: list[str]
    bairro: list[str]
    categoria: list[str]


class MetaResposta(BaseModel):
    fonte: list[str]
    periodo: PeriodoResposta
    filtros: FiltrosAplicadosResposta
    n: int
    atualizado_em: datetime | None

    @classmethod
    def de_procedencia(cls, procedencia: Procedencia) -> "MetaResposta":
        filtros = procedencia.filtros
        return cls(
            fonte=list(procedencia.fontes),
            periodo=PeriodoResposta(inicio=filtros.ano_inicio, fim=filtros.ano_fim),
            filtros=FiltrosAplicadosResposta(
                rpa=list(filtros.rpas),
                bairro=list(filtros.bairros),
                categoria=list(filtros.categorias),
            ),
            n=procedencia.n,
            atualizado_em=procedencia.atualizado_em,
        )


class Resposta[T](BaseModel):
    dados: T
    meta: MetaResposta
