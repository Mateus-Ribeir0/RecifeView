from pydantic import BaseModel, Field

from app.domain.conta import DIGITOS_DO_CODIGO, TAMANHO_MAXIMO_DO_NOME
from app.domain.email import TAMANHO_MAXIMO_DO_EMAIL
from app.domain.senha import TAMANHO_MAXIMO_DA_SENHA

PADRAO_DO_CODIGO = rf"^\d{{{DIGITOS_DO_CODIGO}}}$"
Email = Field(min_length=3, max_length=TAMANHO_MAXIMO_DO_EMAIL)
Senha = Field(min_length=1, max_length=TAMANHO_MAXIMO_DA_SENHA)


class NovaContaEntrada(BaseModel):
    nome: str = Field(max_length=TAMANHO_MAXIMO_DO_NOME * 2)
    email: str = Email
    senha: str = Senha
    bairro_oficial: str | None = Field(default=None, max_length=60)
    aceitou_os_termos: bool
    site: str = Field(default="", max_length=200)


class EmailEntrada(BaseModel):
    email: str = Email


class NovaSenhaEntrada(BaseModel):
    email: str = Email
    codigo: str = Field(pattern=PADRAO_DO_CODIGO)
    nova_senha: str = Senha


class AtualizacaoDaContaEntrada(BaseModel):
    nome: str = Field(max_length=TAMANHO_MAXIMO_DO_NOME * 2)
    bairro_oficial: str | None = Field(default=None, max_length=60)


class ExclusaoDaContaEntrada(BaseModel):
    senha: str = Senha


class PedidoRecebidoResposta(BaseModel):
    mensagem: str
