from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, PlainSerializer, WithJsonSchema

from app.domain.procedencia import Procedencia

# A chave é um hash de 64 bits: como número, o navegador perderia os últimos dígitos.
ChaveDoRegistro = Annotated[
    int,
    PlainSerializer(str, return_type=str),
    WithJsonSchema({"type": "string", "pattern": "^-?[0-9]+$"}),
]


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
