from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.acesso_corporativo import AcessoCorporativo, ConviteDeAcesso


class ConviteRepository(Protocol):
    def adicionar(self, convite: ConviteDeAcesso, criado_por: UUID | None) -> None: ...

    def buscar_pelo_hash(self, hash_do_token: str) -> ConviteDeAcesso | None: ...

    def marcar_usado(self, convite_id: UUID, agora: datetime) -> None: ...

    def encerrar_os_abertos(self, usuario_id: UUID, agora: datetime) -> None: ...


class AcessosCorporativosRepository(Protocol):
    def listar(self) -> list[AcessoCorporativo]: ...

    def buscar(self, usuario_id: UUID) -> AcessoCorporativo | None: ...
