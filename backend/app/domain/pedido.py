from dataclasses import dataclass
from datetime import date, datetime

from app.domain.encaminhamento.encaminhamento import Encaminhamento
from app.domain.erros import LimiteDePedidosAtingido

LIMITE_DE_PEDIDOS_ACOMPANHADOS = 20
REGISTROS_POR_PROTOCOLO = 5


@dataclass(frozen=True)
class RegistroDoPedido:
    """O que a fonte publica sobre um pedido. Nunca o endereço, o texto nem o pseudônimo."""

    chave_registro: int
    fonte: str
    protocolo: str
    data_abertura: date | None = None
    categoria: str | None = None
    servico: str | None = None
    tipo_registro: str | None = None
    orgao: str | None = None
    situacao: str | None = None
    data_ult_movimento: date | None = None
    prazo_da_fonte: date | None = None
    bairro_oficial: str | None = None
    rpa: str | None = None


@dataclass(frozen=True)
class AndamentoDoPedido:
    registro: RegistroDoPedido
    encaminhamentos: tuple[Encaminhamento, ...] = ()


@dataclass(frozen=True)
class PedidoAcompanhado:
    id: int
    protocolo: str
    criado_em: datetime


def exigir_espaco_para_acompanhar(acompanhados: int) -> None:
    if acompanhados >= LIMITE_DE_PEDIDOS_ACOMPANHADOS:
        raise LimiteDePedidosAtingido
