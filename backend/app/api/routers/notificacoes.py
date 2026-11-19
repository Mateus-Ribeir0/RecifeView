from fastapi import APIRouter, status

from app.api.dependencias import UsuarioAtualDep
from app.api.dependencias_corporativas import NotificacoesDaContaDep
from app.api.schemas.erros import ErroResposta
from app.api.schemas.notificacoes import CaixaDeNotificacoesResposta

roteador = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@roteador.get(
    "",
    summary="As notificações mais recentes da conta e quantas ainda não foram lidas",
    description="Serve aos três perfis. Cada conta vê só as próprias notificações.",
)
def consultar(
    usuario: UsuarioAtualDep, notificacoes: NotificacoesDaContaDep
) -> CaixaDeNotificacoesResposta:
    return CaixaDeNotificacoesResposta.de_caixa(notificacoes.consultar(usuario.id))


@roteador.post(
    "/{notificacao_id}/leitura",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marca uma notificação como lida",
    responses={404: {"model": ErroResposta, "description": "Notificação não encontrada"}},
)
def marcar_como_lida(
    notificacao_id: int, usuario: UsuarioAtualDep, notificacoes: NotificacoesDaContaDep
) -> None:
    notificacoes.marcar_como_lida(usuario.id, notificacao_id)


@roteador.post(
    "/leitura",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marca todas as notificações da conta como lidas",
)
def marcar_todas_como_lidas(usuario: UsuarioAtualDep, notificacoes: NotificacoesDaContaDep) -> None:
    notificacoes.marcar_todas_como_lidas(usuario.id)
