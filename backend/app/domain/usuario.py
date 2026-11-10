from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self
from uuid import UUID

from app.domain.email import Email

TENTATIVAS_ANTES_DO_BLOQUEIO = 5
NOME_DA_CONTA_EXCLUIDA = "Conta excluída"
DURACAO_DO_BLOQUEIO = timedelta(minutes=15)


class Perfil(StrEnum):
    GESTOR = "GESTOR"
    ADMINISTRADOR = "ADMINISTRADOR"
    CIDADAO = "CIDADAO"


PERFIS_DA_GESTAO = frozenset({Perfil.GESTOR, Perfil.ADMINISTRADOR})


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
    bairro_oficial: str | None = None

    @property
    def e_da_gestao(self) -> bool:
        return self.perfil in PERFIS_DA_GESTAO

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

    def com_dados_pessoais(self, nome: str, bairro_oficial: str | None) -> Self:
        return replace(self, nome=nome, bairro_oficial=bairro_oficial)

    def excluido(self, email_anonimo: Email, hash_inutil: str) -> Self:
        """Mantém a linha para a auditoria, sem nada que identifique a pessoa."""
        return replace(
            self,
            email=email_anonimo,
            nome=NOME_DA_CONTA_EXCLUIDA,
            hash_da_senha=hash_inutil,
            ativo=False,
            bairro_oficial=None,
        )

    def com_senha_temporaria(self, hash_da_senha: str) -> Self:
        return replace(
            self,
            hash_da_senha=hash_da_senha,
            deve_trocar_senha=True,
            tentativas_falhas=0,
            bloqueado_ate=None,
        )
