from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ConsultaAuditada:
    usuario_id: UUID
    rota: str
    filtros: dict[str, Any]
    ocorrida_em: datetime
