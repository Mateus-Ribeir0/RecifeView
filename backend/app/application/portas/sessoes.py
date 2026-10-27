from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.sessao import Sessao


class SessaoRepository(Protocol):
    def adicionar(self, sessao: Sessao) -> None: ...

    def buscar_por_hash_do_token(self, hash_do_token: str) -> Sessao | None: ...

    def atualizar(self, sessao: Sessao) -> None: ...

    def revogar_todas_do_usuario(self, usuario_id: UUID, agora: datetime) -> None: ...
