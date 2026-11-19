from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.application.casos_de_uso.acessos_corporativos.convite import ConviteAberto
from app.domain.acesso_corporativo import AcessoCorporativo, SituacaoDoAcesso
from app.domain.conta import TAMANHO_MAXIMO_DO_NOME
from app.domain.email import TAMANHO_MAXIMO_DO_EMAIL
from app.domain.encaminhamento.orgaos import Orgao, nome_do_orgao

TAMANHO_MAXIMO_DO_TOKEN = 100
TAMANHO_MAXIMO_DA_SENHA = 128
FOLGA_PARA_ESPACOS = 20


class AcessoCorporativoResposta(BaseModel):
    id: UUID
    nome: str
    email: str
    orgao: Orgao
    nome_do_orgao: str
    situacao: SituacaoDoAcesso
    criado_em: datetime
    convite_expira_em: datetime | None
    ultimo_acesso_em: datetime | None

    @classmethod
    def de_acesso(cls, acesso: AcessoCorporativo, agora: datetime) -> "AcessoCorporativoResposta":
        return cls(
            id=acesso.usuario_id,
            nome=acesso.nome,
            email=acesso.email,
            orgao=acesso.orgao,
            nome_do_orgao=nome_do_orgao(acesso.orgao),
            situacao=acesso.situacao(agora),
            criado_em=acesso.criado_em,
            convite_expira_em=acesso.convite_expira_em,
            ultimo_acesso_em=acesso.ultimo_acesso_em,
        )


class ListaDeAcessosResposta(BaseModel):
    pode_alterar: bool
    itens: list[AcessoCorporativoResposta]


class DadosDoAcessoEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DO_NOME + FOLGA_PARA_ESPACOS)
    orgao: Orgao


class NovoAcessoEntrada(DadosDoAcessoEntrada):
    email: str = Field(min_length=3, max_length=TAMANHO_MAXIMO_DO_EMAIL)


class TokenDoConviteEntrada(BaseModel):
    token: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DO_TOKEN)


class AceiteDoConviteEntrada(TokenDoConviteEntrada):
    senha: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DA_SENHA)


class ConviteResposta(BaseModel):
    nome: str
    email: str
    orgao: Orgao
    nome_do_orgao: str
    expira_em: datetime

    @classmethod
    def de_convite(cls, convite: ConviteAberto) -> "ConviteResposta":
        return cls(
            nome=convite.nome,
            email=convite.email,
            orgao=convite.orgao,
            nome_do_orgao=nome_do_orgao(convite.orgao),
            expira_em=convite.expira_em,
        )
