from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self
from uuid import UUID

from app.domain.email import Email

TENTATIVAS_ANTES_DO_BLOQUEIO = 5
DURACAO_DO_BLOQUEIO = timedelta(minutes=15)


class Perfil(StrEnum):
    GESTOR = "GESTOR"
    ADMINISTRADOR = "ADMINISTRADOR"


@dataclass(frozen=True)
class Usuario:
    id: UUID
    email: Email
    nome: str
    perfil: Perfil
    hash_da_senha: str
    ativo: bool = True
    deve_trocar_senha: bool = True
    tentativas_falhas: int = 0
    bloqueado_ate: datetime | None = None

    def fim_do_bloqueio(self, agora: datetime) -> datetime | None:
        if self.bloqueado_ate is not None and agora < self.bloqueado_ate:
            return self.bloqueado_ate
        return None

    def com_falha_de_entrada(self, agora: datetime) -> Self:
        tentativas = self.tentativas_falhas + 1
        if tentativas < TENTATIVAS_ANTES_DO_BLOQUEIO:
            return replace(self, tentativas_falhas=tentativas)
        return replace(self, tentativas_falhas=0, bloqueado_ate=agora + DURACAO_DO_BLOQUEIO)

    def com_entrada_aceita(self) -> Self:
        return replace(self, tentativas_falhas=0, bloqueado_ate=None)

    def com_nova_senha(self, hash_da_senha: str) -> Self:
        return replace(
            self,
            hash_da_senha=hash_da_senha,
            deve_trocar_senha=False,
            tentativas_falhas=0,
            bloqueado_ate=None,
        )

    def com_senha_temporaria(self, hash_da_senha: str) -> Self:
        return replace(
            self,
            hash_da_senha=hash_da_senha,
            deve_trocar_senha=True,
            tentativas_falhas=0,
            bloqueado_ate=None,
        )
