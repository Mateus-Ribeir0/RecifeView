from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.schemas.erros import DetalheDoErro, ErroResposta
from app.application.portas.contas import EnvioDeEmailFalhou
from app.domain.erros import (
    AcessoNegado,
    AreaDaGestaoNegada,
    ArquivoGrandeDemais,
    ArquivoIlegivel,
    ArquivoVazio,
    CadastroInvalido,
    CodigoInvalido,
    ContaBloqueada,
    ContaInativa,
    ContribuicaoInvalida,
    CredenciaisInvalidas,
    DecisaoInvalida,
    DiaForaDaJanela,
    EmailInvalido,
    EmailJaCadastrado,
    EncaminhamentoInvalido,
    EncaminhamentoNaoEncontrado,
    EnviosDemais,
    ErroDeDominio,
    ImportacaoEmEstadoInvalido,
    ImportacaoNaoEncontrada,
    ImportacaoNaoPodeSerDesfeita,
    LinkDeRetornoInvalido,
    OcorrenciaJaEncaminhada,
    OcorrenciaNaoEncontrada,
    PacoteVazio,
    ParNaoEncontrado,
    PenteFinoPendente,
    PeriodoInvalido,
    ProtocoloInvalido,
    SenhaAtualIncorreta,
    SenhaFraca,
    SessaoInvalida,
    TentativasDemais,
    TransicaoInvalida,
    UsuarioNaoEncontrado,
    ValorDeFiltroInvalido,
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
    ImportacaoNaoEncontrada: RespostaDeErro(
        status.HTTP_404_NOT_FOUND, "importacao_nao_encontrada", "Importação não encontrada."
    ),
    ImportacaoEmEstadoInvalido: RespostaDeErro(
        status.HTTP_409_CONFLICT,
        "importacao_em_outra_etapa",
        "A importação não está mais nesta etapa. Atualize a página.",
    ),
    ImportacaoNaoPodeSerDesfeita: RespostaDeErro(
        status.HTTP_409_CONFLICT,
        "importacao_nao_pode_ser_desfeita",
        "Só a importação mais recente pode ser desfeita.",
    ),
    ArquivoVazio: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "arquivo_vazio", "O arquivo está vazio."
    ),
    ArquivoIlegivel: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "arquivo_ilegivel",
        "Não foi possível ler o arquivo. Confira o formato.",
    ),
    ArquivoGrandeDemais: RespostaDeErro(
        status.HTTP_413_CONTENT_TOO_LARGE,
        "arquivo_grande_demais",
        "O arquivo passa do tamanho máximo aceito.",
    ),
    DecisaoInvalida: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "decisao_invalida", "Confira as escolhas feitas."
    ),
    PeriodoInvalido: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "periodo_invalido",
        "O início do período precisa vir antes do fim.",
    ),
    ValorDeFiltroInvalido: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "filtro_invalido", "Confira os filtros aplicados."
    ),
    DiaForaDaJanela: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "dia_fora_da_janela",
        "Não há dados para o dia escolhido.",
    ),
    AcessoNegado: RespostaDeErro(
        status.HTTP_403_FORBIDDEN,
        "acesso_negado",
        "Esta área é só da gestão. A sua conta tem acesso à área do cidadão.",
    ),
    AreaDaGestaoNegada: RespostaDeErro(
        status.HTTP_403_FORBIDDEN,
        "area_da_gestao_negada",
        "Esta conta não tem acesso à área da gestão. Entre pela área do cidadão.",
    ),
    CodigoInvalido: RespostaDeErro(
        status.HTTP_400_BAD_REQUEST,
        "codigo_invalido",
        "Código, e-mail ou senha não conferem, ou o código venceu. Confira ou peça um novo.",
    ),
    CadastroInvalido: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "cadastro_invalido", "Confira os campos."
    ),
    TentativasDemais: RespostaDeErro(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "tentativas_demais",
        "Muitas tentativas em pouco tempo. Espere alguns minutos e tente de novo.",
    ),
    ContribuicaoInvalida: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "contribuicao_invalida", "Confira os campos."
    ),
    EnviosDemais: RespostaDeErro(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "envios_demais",
        "Muitos relatos em pouco tempo. Tente de novo em alguns minutos.",
    ),
    ParNaoEncontrado: RespostaDeErro(
        status.HTTP_404_NOT_FOUND,
        "par_nao_encontrado",
        "Esta dupla já foi decidida. Atualize a página.",
    ),
    PenteFinoPendente: RespostaDeErro(
        status.HTTP_409_CONFLICT,
        "pente_fino_pendente",
        "Ainda há relatos parecidos sem decisão. Revise todos antes de gerar o pacote.",
    ),
    PacoteVazio: RespostaDeErro(
        status.HTTP_409_CONFLICT, "pacote_vazio", "Não há ocorrências novas para gerar um pacote."
    ),
    ProtocoloInvalido: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "protocolo_invalido",
        "Confira o protocolo: de 4 a 40 caracteres, só letras, números, ponto, barra e hífen.",
    ),
    OcorrenciaNaoEncontrada: RespostaDeErro(
        status.HTTP_404_NOT_FOUND,
        "ocorrencia_nao_encontrada",
        "Esta ocorrência não está mais na base. Atualize a fila.",
    ),
    OcorrenciaJaEncaminhada: RespostaDeErro(
        status.HTTP_409_CONFLICT,
        "ocorrencia_ja_encaminhada",
        "Esta ocorrência já tem um encaminhamento aberto. Espere o retorno do órgão.",
    ),
    EncaminhamentoNaoEncontrado: RespostaDeErro(
        status.HTTP_404_NOT_FOUND,
        "encaminhamento_nao_encontrado",
        "Encaminhamento não encontrado.",
    ),
    EncaminhamentoInvalido: RespostaDeErro(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "encaminhamento_invalido", "Confira os campos."
    ),
    TransicaoInvalida: RespostaDeErro(
        status.HTTP_409_CONFLICT,
        "resposta_fora_de_ordem",
        "A situação do encaminhamento mudou e não aceita esta resposta. Atualize a página.",
    ),
    LinkDeRetornoInvalido: RespostaDeErro(
        status.HTTP_404_NOT_FOUND,
        "link_de_retorno_invalido",
        "Este link venceu ou não existe. Peça um novo à gestão que encaminhou a ocorrência.",
    ),
}


ENVIO_DE_EMAIL_INDISPONIVEL = DetalheDoErro(
    codigo="envio_de_email_indisponivel",
    mensagem=(
        "Não conseguimos enviar o e-mail agora. Nada foi gravado: tente de novo em alguns minutos."
    ),
)


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    app.add_exception_handler(ErroDeDominio, _tratar_erro_de_dominio)  # type: ignore[arg-type]
    app.add_exception_handler(EnvioDeEmailFalhou, _tratar_envio_de_email_falhou)
    app.add_exception_handler(RequestValidationError, _tratar_dados_invalidos)  # type: ignore[arg-type]


def _tratar_erro_de_dominio(_: Request, erro: ErroDeDominio) -> JSONResponse:
    resposta = RESPOSTAS_POR_ERRO.get(type(erro), ERRO_GENERICO)
    com_motivo = (
        SenhaFraca,
        DecisaoInvalida,
        ContribuicaoInvalida,
        CadastroInvalido,
        EncaminhamentoInvalido,
    )
    mensagem = erro.motivo if isinstance(erro, com_motivo) else resposta.mensagem
    detalhes = _detalhes_do_erro(erro)
    return _responder(
        resposta.status, DetalheDoErro(codigo=resposta.codigo, mensagem=mensagem, detalhes=detalhes)
    )


def _detalhes_do_erro(erro: ErroDeDominio) -> dict[str, Any] | None:
    if isinstance(erro, ContaBloqueada):
        return {"desbloqueio_em": erro.desbloqueio_em.isoformat()}
    if isinstance(erro, (ContribuicaoInvalida, CadastroInvalido, EncaminhamentoInvalido)):
        return {"campo": erro.campo}
    return None


def _tratar_envio_de_email_falhou(_: Request, __: Exception) -> JSONResponse:
    return _responder(status.HTTP_503_SERVICE_UNAVAILABLE, ENVIO_DE_EMAIL_INDISPONIVEL)


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
