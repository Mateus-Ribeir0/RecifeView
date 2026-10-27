from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self
from uuid import UUID


@dataclass(frozen=True)
class Sessao:
    id: UUID
    usuario_id: UUID
    hash_do_token: str
    criada_em: datetime
    expira_em: datetime
    revogada_em: datetime | None = None

    def esta_ativa(self, agora: datetime) -> bool:
        return self.revogada_em is None and agora < self.expira_em

    def revogada(self, agora: datetime) -> Self:
        return replace(self, revogada_em=agora)
