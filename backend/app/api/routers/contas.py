from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.api.cookies import apagar_cookie_de_sessao, gravar_cookie_de_sessao
from app.api.dependencias import (
    BairrosOficiaisDep,
    ConfiguracaoDep,
    ServicosDeContaDep,
    UsuarioAtualDep,
    limitar_operacoes_de_conta,
)
from app.api.schemas.autenticacao import AcessoResposta, UsuarioResposta
from app.api.schemas.contas import (
    AtualizacaoDaContaEntrada,
    ConfirmacaoEntrada,
    EmailEntrada,
    ExclusaoDaContaEntrada,
    NovaContaEntrada,
    NovaSenhaEntrada,
    PedidoRecebidoResposta,
)
from app.api.schemas.erros import ErroResposta
from app.application.casos_de_uso.contas.confirmar_email import (
    ConfirmacaoDeEmail,
    ConfirmarEmail,
)
from app.application.casos_de_uso.contas.criar_conta import CriarConta, NovaConta
from app.application.casos_de_uso.contas.minha_conta import (
    AtualizarMinhaConta,
    ExcluirMinhaConta,
)
from app.application.casos_de_uso.contas.recuperar_senha import (
    CriarNovaSenha,
    NovaSenhaComCodigo,
    PedirNovaSenha,
)
from app.application.casos_de_uso.contas.reenviar_codigo import ReenviarCodigoDeConfirmacao

roteador = APIRouter(prefix="/contas", tags=["Contas de cidadão"])

LIMITADA = [Depends(limitar_operacoes_de_conta)]
RESPOSTA_DO_CADASTRO = (
    "Se o e-mail puder ser usado, enviamos um código de 6 dígitos. Ele vale por 15 minutos."
)
RESPOSTA_DO_REENVIO = "Se houver um cadastro esperando confirmação, enviamos um novo código."
RESPOSTA_DA_RECUPERACAO = "Se o e-mail tiver uma conta de cidadão, enviamos um código."
MUITAS_TENTATIVAS: dict[int | str, dict[str, Any]] = {
    429: {"model": ErroResposta, "description": "Muitas tentativas"}
}


@roteador.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=LIMITADA,
    summary="Cria uma conta de cidadão e envia o código de confirmação",
    description="A resposta é a mesma para e-mail novo e e-mail que já tem conta.",
    responses={422: {"model": ErroResposta}, **MUITAS_TENTATIVAS},
)
def criar_conta(
    dados: NovaContaEntrada, servicos: ServicosDeContaDep, bairros: BairrosOficiaisDep
) -> PedidoRecebidoResposta:
    if not dados.site:
        nova = NovaConta(
            dados.nome, dados.email, dados.senha, dados.bairro_oficial, dados.aceitou_os_termos
        )
        CriarConta(servicos, bairros).executar(nova)
    return PedidoRecebidoResposta(mensagem=RESPOSTA_DO_CADASTRO)


@roteador.post(
    "/confirmar",
    dependencies=LIMITADA,
    summary="Confirma o e-mail com o código e a senha, e já entra na conta",
    responses={400: {"model": ErroResposta, "description": "Código incorreto ou vencido"}},
)
def confirmar(
    dados: ConfirmacaoEntrada,
    resposta: Response,
    servicos: ServicosDeContaDep,
    configuracao: ConfiguracaoDep,
) -> AcessoResposta:
    confirmacao = ConfirmacaoDeEmail(dados.email, dados.codigo, dados.senha)
    sessao = ConfirmarEmail(servicos).executar(confirmacao)
    gravar_cookie_de_sessao(resposta, sessao, configuracao.cookie_seguro)
    return AcessoResposta.de_acesso(sessao.acesso)


@roteador.post(
    "/reenviar-codigo",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=LIMITADA,
    summary="Envia outro código de confirmação",
    responses=MUITAS_TENTATIVAS,
)
def reenviar_codigo(dados: EmailEntrada, servicos: ServicosDeContaDep) -> PedidoRecebidoResposta:
    ReenviarCodigoDeConfirmacao(servicos).executar(dados.email)
    return PedidoRecebidoResposta(mensagem=RESPOSTA_DO_REENVIO)


@roteador.post(
    "/recuperar-senha",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=LIMITADA,
    summary="Envia um código para criar uma nova senha",
    responses=MUITAS_TENTATIVAS,
)
def recuperar_senha(dados: EmailEntrada, servicos: ServicosDeContaDep) -> PedidoRecebidoResposta:
    PedirNovaSenha(servicos).executar(dados.email)
    return PedidoRecebidoResposta(mensagem=RESPOSTA_DA_RECUPERACAO)


@roteador.post(
    "/nova-senha",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=LIMITADA,
    summary="Cria uma nova senha com o código recebido",
    responses={400: {"model": ErroResposta}, 422: {"model": ErroResposta}},
)
def nova_senha(dados: NovaSenhaEntrada, servicos: ServicosDeContaDep) -> None:
    CriarNovaSenha(servicos).executar(
        NovaSenhaComCodigo(dados.email, dados.codigo, dados.nova_senha)
    )


@roteador.put("/eu", summary="Atualiza o nome e o bairro da conta")
def atualizar(
    dados: AtualizacaoDaContaEntrada,
    usuario: UsuarioAtualDep,
    servicos: ServicosDeContaDep,
    bairros: BairrosOficiaisDep,
) -> UsuarioResposta:
    atualizado = AtualizarMinhaConta(servicos, bairros).executar(
        usuario, dados.nome, dados.bairro_oficial
    )
    return UsuarioResposta.de_usuario(atualizado)


@roteador.post(
    "/eu/excluir",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui a conta de cidadão",
    responses={400: {"model": ErroResposta, "description": "Senha incorreta"}},
)
def excluir(
    dados: ExclusaoDaContaEntrada,
    resposta: Response,
    usuario: UsuarioAtualDep,
    servicos: ServicosDeContaDep,
    configuracao: ConfiguracaoDep,
) -> None:
    ExcluirMinhaConta(servicos).executar(usuario, dados.senha)
    apagar_cookie_de_sessao(resposta, configuracao.cookie_seguro)
