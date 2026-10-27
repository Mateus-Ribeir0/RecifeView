from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field

from app.application.sessoes import AcessoConcedido
from app.domain.email import TAMANHO_MAXIMO_DO_EMAIL
from app.domain.senha import TAMANHO_MAXIMO_DA_SENHA
from app.domain.usuario import Perfil, Usuario


class CredenciaisDeEntrada(BaseModel):
    email: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DO_EMAIL)
    senha: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DA_SENHA)


class TrocaDeSenha(BaseModel):
    senha_atual: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DA_SENHA)
    nova_senha: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DA_SENHA)


class UsuarioResposta(BaseModel):
    id: UUID
    nome: str
    email: str
    perfil: Perfil
    deve_trocar_senha: bool

    @classmethod
    def de_usuario(cls, usuario: Usuario) -> Self:
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=str(usuario.email),
            perfil=usuario.perfil,
            deve_trocar_senha=usuario.deve_trocar_senha,
        )


class AcessoResposta(BaseModel):
    token_de_acesso: str
    expira_em: datetime
    usuario: UsuarioResposta

    @classmethod
    def de_acesso(cls, acesso: AcessoConcedido) -> Self:
        return cls(
            token_de_acesso=acesso.token_de_acesso.valor,
            expira_em=acesso.token_de_acesso.expira_em,
            usuario=UsuarioResposta.de_usuario(acesso.usuario),
        )
