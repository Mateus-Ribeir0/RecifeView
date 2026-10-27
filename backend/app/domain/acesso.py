from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class TipoDeEventoDeAcesso(StrEnum):
    ENTRADA = "ENTRADA"
    ENTRADA_RECUSADA = "ENTRADA_RECUSADA"
    CONTA_BLOQUEADA = "CONTA_BLOQUEADA"
    SAIDA = "SAIDA"
    SENHA_ALTERADA = "SENHA_ALTERADA"
    SENHA_REDEFINIDA = "SENHA_REDEFINIDA"


@dataclass(frozen=True)
class EventoDeAcesso:
    tipo: TipoDeEventoDeAcesso
    ocorrido_em: datetime
    usuario_id: UUID | None = None
