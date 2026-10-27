from fastapi import Response

from app.application.sessoes import SessaoAberta

NOME_DO_COOKIE_DE_SESSAO = "rv_sessao"
CAMINHO_DO_COOKIE_DE_SESSAO = "/api/v1/autenticacao"


def gravar_cookie_de_sessao(resposta: Response, sessao: SessaoAberta, seguro: bool) -> None:
    resposta.set_cookie(
        NOME_DO_COOKIE_DE_SESSAO,
        sessao.token_de_sessao,
        max_age=int(sessao.validade.total_seconds()),
        path=CAMINHO_DO_COOKIE_DE_SESSAO,
        httponly=True,
        secure=seguro,
        samesite="strict",
    )


def apagar_cookie_de_sessao(resposta: Response, seguro: bool) -> None:
    resposta.delete_cookie(
        NOME_DO_COOKIE_DE_SESSAO,
        path=CAMINHO_DO_COOKIE_DE_SESSAO,
        httponly=True,
        secure=seguro,
        samesite="strict",
    )
