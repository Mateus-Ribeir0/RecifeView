from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.schemas.erros import DetalheDoErro, ErroResposta
from app.domain.erros import (
    ContaBloqueada,
    ContaInativa,
    CredenciaisInvalidas,
    EmailInvalido,
    EmailJaCadastrado,
    ErroDeDominio,
    SenhaAtualIncorreta,
    SenhaFraca,
    SessaoInvalida,
    UsuarioNaoEncontrado,
)


@dataclass(frozen=True)
class RespostaDeErro:
    status: int
    codigo: str
    mensagem: str


ERRO_GENERICO = RespostaDeErro(
    status.HTTP_400_BAD_REQUEST, "requisicao_recusada", "Não foi possível concluir a operação."
)

RESPOSTAS_POR_ERRO: dict[type[ErroDeDominio], RespostaDeErro] = {
    CredenciaisInvalidas: RespostaDeErro(
        status.HTTP_401_UNAUTHORIZED, "credenciais_invalidas", "E-mail ou senha incorretos."
    ),
    SessaoInvalida: RespostaDeErro(
        status.HTTP_401_UNAUTHORIZED,
        "sessao_invalida",
        "Sua sessão terminou. Entre de novo para continuar.",
    ),
    ContaInativa: RespostaDeErro(
        status.HTTP_403_FORBIDDEN,
        "conta_inativa",
        "Esta conta está desativada. Fale com a administração do RecifeView.",
    ),
    ContaBloqueada: RespostaDeErro(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "conta_bloqueada",
        "Muitas tentativas sem sucesso. Por segurança, a conta ficou bloqueada por alguns minutos.",
    ),
    SenhaAtualIncorreta: RespostaDeErro(
        status.HTTP_400_BAD_REQUEST, "senha_atual_incorreta", "A senha atual não confere."
    ),
    SenhaFraca: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "senha_fraca", "A nova senha não atende às regras."
    ),
    EmailInvalido: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "email_invalido", "Informe um e-mail válido."
    ),
    EmailJaCadastrado: RespostaDeErro(
        status.HTTP_409_CONFLICT, "email_ja_cadastrado", "Já existe uma conta com este e-mail."
    ),
    UsuarioNaoEncontrado: RespostaDeErro(
        status.HTTP_404_NOT_FOUND, "usuario_nao_encontrado", "Conta não encontrada."
    ),
}


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    app.add_exception_handler(ErroDeDominio, _tratar_erro_de_dominio)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _tratar_dados_invalidos)  # type: ignore[arg-type]


def _tratar_erro_de_dominio(_: Request, erro: ErroDeDominio) -> JSONResponse:
    resposta = RESPOSTAS_POR_ERRO.get(type(erro), ERRO_GENERICO)
    mensagem = erro.motivo if isinstance(erro, SenhaFraca) else resposta.mensagem
    detalhes = _detalhes_do_erro(erro)
    return _responder(
        resposta.status, DetalheDoErro(codigo=resposta.codigo, mensagem=mensagem, detalhes=detalhes)
    )


def _detalhes_do_erro(erro: ErroDeDominio) -> dict[str, Any] | None:
    if isinstance(erro, ContaBloqueada):
        return {"desbloqueio_em": erro.desbloqueio_em.isoformat()}
    return None


def _tratar_dados_invalidos(_: Request, erro: RequestValidationError) -> JSONResponse:
    campos = sorted({str(problema["loc"][-1]) for problema in erro.errors()})
    detalhe = DetalheDoErro(
        codigo="dados_invalidos",
        mensagem="Confira os campos enviados.",
        detalhes={"campos": campos},
    )
    return _responder(status.HTTP_422_UNPROCESSABLE_CONTENT, detalhe)


def _responder(codigo_http: int, detalhe: DetalheDoErro) -> JSONResponse:
    corpo = ErroResposta(erro=detalhe).model_dump(mode="json", exclude_none=True)
    return JSONResponse(status_code=codigo_http, content=corpo)
