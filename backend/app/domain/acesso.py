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
    CONTA_CRIADA = "CONTA_CRIADA"
    CODIGO_RECUSADO = "CODIGO_RECUSADO"
    SENHA_RECUPERADA = "SENHA_RECUPERADA"
    CONTA_EXCLUIDA = "CONTA_EXCLUIDA"
    CONVITE_ENVIADO = "CONVITE_ENVIADO"
    CONVITE_ACEITO = "CONVITE_ACEITO"
    CONTA_ALTERADA = "CONTA_ALTERADA"
    CONTA_DESATIVADA = "CONTA_DESATIVADA"
    CONTA_REATIVADA = "CONTA_REATIVADA"


class AreaDeAcesso(StrEnum):
    CIDADE = "cidade"
    GESTAO = "gestao"
    CORPORATIVO = "corporativo"


@dataclass(frozen=True)
class EventoDeAcesso:
    tipo: TipoDeEventoDeAcesso
    ocorrido_em: datetime
    usuario_id: UUID | None = None
