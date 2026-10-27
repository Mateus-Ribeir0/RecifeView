from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.usuario import Usuario


@dataclass(frozen=True)
class TokenDeAcesso:
    valor: str
    expira_em: datetime


class HashDeSenha(Protocol):
    def gerar(self, senha: str) -> str: ...

    def confere(self, senha: str, hash_da_senha: str) -> bool: ...

    def simular_conferencia(self, senha: str) -> None:
        """Gasta o tempo de uma conferência real, para a resposta não revelar se o e-mail existe."""
        ...


class EmissorDeTokenDeAcesso(Protocol):
    def emitir(self, usuario: Usuario, agora: datetime) -> TokenDeAcesso: ...

    def identificar(self, token: str, agora: datetime) -> UUID: ...
