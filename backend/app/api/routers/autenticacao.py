from typing import Annotated

from fastapi import APIRouter, Cookie, Response, status

from app.api.cookies import (
    NOME_DO_COOKIE_DE_SESSAO,
    apagar_cookie_de_sessao,
    gravar_cookie_de_sessao,
)
from app.api.dependencias import (
    ConfiguracaoDep,
    EntrarDep,
    RenovarAcessoDep,
    SairDep,
    TrocarSenhaDep,
    UsuarioAtualDep,
)
from app.api.schemas.autenticacao import (
    AcessoResposta,
    CredenciaisDeEntrada,
    TrocaDeSenha,
    UsuarioResposta,
)
from app.api.schemas.erros import ErroResposta

roteador = APIRouter(prefix="/autenticacao", tags=["Autenticação"])

TokenDeSessao = Annotated[str | None, Cookie(alias=NOME_DO_COOKIE_DE_SESSAO)]


@roteador.post(
    "/entrar",
    summary="Entra no painel com e-mail e senha",
    responses={
        401: {"model": ErroResposta, "description": "E-mail ou senha incorretos"},
        403: {"model": ErroResposta, "description": "Conta desativada"},
        429: {"model": ErroResposta, "description": "Conta bloqueada por tentativas"},
    },
)
def entrar(
    credenciais: CredenciaisDeEntrada,
    resposta: Response,
    entrar: EntrarDep,
    configuracao: ConfiguracaoDep,
) -> AcessoResposta:
    sessao = entrar.executar(credenciais.email, credenciais.senha)
    gravar_cookie_de_sessao(resposta, sessao, configuracao.cookie_seguro)
    return AcessoResposta.de_acesso(sessao.acesso)


@roteador.post(
    "/renovar",
    summary="Emite um novo token de acesso a partir do cookie de sessão",
    responses={401: {"model": ErroResposta, "description": "Sem sessão ativa"}},
)
def renovar(
    renovar_acesso: RenovarAcessoDep, token_de_sessao: TokenDeSessao = None
) -> AcessoResposta:
    return AcessoResposta.de_acesso(renovar_acesso.executar(token_de_sessao))


@roteador.post(
    "/sair",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Encerra a sessão atual",
)
def sair(
    resposta: Response,
    sair: SairDep,
    configuracao: ConfiguracaoDep,
    token_de_sessao: TokenDeSessao = None,
) -> None:
    sair.executar(token_de_sessao)
    apagar_cookie_de_sessao(resposta, configuracao.cookie_seguro)


@roteador.get(
    "/eu",
    summary="Devolve o usuário dono do token de acesso",
    responses={401: {"model": ErroResposta, "description": "Token ausente ou expirado"}},
)
def eu(usuario: UsuarioAtualDep) -> UsuarioResposta:
    return UsuarioResposta.de_usuario(usuario)


@roteador.post(
    "/trocar-senha",
    summary="Troca a senha e abre uma sessão nova",
    responses={
        400: {"model": ErroResposta, "description": "Senha atual incorreta"},
        401: {"model": ErroResposta, "description": "Token ausente ou expirado"},
        422: {"model": ErroResposta, "description": "Nova senha fora das regras"},
    },
)
def trocar_senha(
    dados: TrocaDeSenha,
    resposta: Response,
    usuario: UsuarioAtualDep,
    trocar_senha: TrocarSenhaDep,
    configuracao: ConfiguracaoDep,
) -> AcessoResposta:
    sessao = trocar_senha.executar(usuario, dados.senha_atual, dados.nova_senha)
    gravar_cookie_de_sessao(resposta, sessao, configuracao.cookie_seguro)
    return AcessoResposta.de_acesso(sessao.acesso)
