from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.encaminhamento.encaminhamento import Encaminhamento
from app.domain.pedido import PedidoAcompanhado, RegistroDoPedido


class ConsultaDePedidos(Protocol):
    def registros(self, protocolo: str) -> list[RegistroDoPedido]: ...


class HistoricoDeEncaminhamentos(Protocol):
    def da_ocorrencia(self, chave_registro: int) -> list[Encaminhamento]: ...


class PedidoAcompanhadoRepository(Protocol):
    def listar(self, usuario_id: UUID) -> list[PedidoAcompanhado]: ...

    def adicionar(self, usuario_id: UUID, protocolo: str, agora: datetime) -> PedidoAcompanhado: ...

    def remover(self, usuario_id: UUID, pedido_id: int) -> None: ...

    def remover_todos(self, usuario_id: UUID) -> None: ...
