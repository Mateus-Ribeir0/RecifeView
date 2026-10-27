from typing import Protocol
from uuid import UUID

from app.domain.email import Email
from app.domain.usuario import Usuario


class UsuarioRepository(Protocol):
    def buscar_por_email(self, email: Email) -> Usuario | None: ...

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None: ...

    def adicionar(self, usuario: Usuario) -> None: ...

    def atualizar(self, usuario: Usuario) -> None: ...
