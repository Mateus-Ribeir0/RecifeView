from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.notificacao import CaixaDeNotificacoes, NovaNotificacao


class NotificacaoRepository(Protocol):
    def criar(self, nova: NovaNotificacao) -> None: ...

    def caixa_do_usuario(self, usuario_id: UUID, limite: int) -> CaixaDeNotificacoes: ...

    def marcar_lida(self, usuario_id: UUID, notificacao_id: int, agora: datetime) -> None: ...

    def marcar_todas_lidas(self, usuario_id: UUID, agora: datetime) -> None: ...
