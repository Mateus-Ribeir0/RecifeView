from dataclasses import dataclass
from uuid import UUID

from app.application.portas.notificacoes import NotificacaoRepository
from app.application.portas.relogio import Relogio
from app.domain.notificacao import NOTIFICACOES_MOSTRADAS, CaixaDeNotificacoes


@dataclass(frozen=True)
class NotificacoesDaConta:
    """Cada conta só lê e marca as próprias notificações."""

    notificacoes: NotificacaoRepository
    relogio: Relogio

    def consultar(self, usuario_id: UUID) -> CaixaDeNotificacoes:
        return self.notificacoes.caixa_do_usuario(usuario_id, NOTIFICACOES_MOSTRADAS)

    def marcar_como_lida(self, usuario_id: UUID, notificacao_id: int) -> None:
        self.notificacoes.marcar_lida(usuario_id, notificacao_id, self.relogio.agora())

    def marcar_todas_como_lidas(self, usuario_id: UUID) -> None:
        self.notificacoes.marcar_todas_lidas(usuario_id, self.relogio.agora())
