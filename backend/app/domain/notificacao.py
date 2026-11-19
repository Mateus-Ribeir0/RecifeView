from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

NOTIFICACOES_MOSTRADAS = 30


@dataclass(frozen=True)
class NovaNotificacao:
    usuario_id: UUID
    titulo: str
    texto: str
    caminho: str


@dataclass(frozen=True)
class Notificacao:
    id: int
    titulo: str
    texto: str
    caminho: str
    criada_em: datetime
    lida_em: datetime | None = None

    @property
    def foi_lida(self) -> bool:
        return self.lida_em is not None


@dataclass(frozen=True)
class CaixaDeNotificacoes:
    nao_lidas: int
    itens: list[Notificacao]
