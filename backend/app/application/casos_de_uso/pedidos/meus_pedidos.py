from dataclasses import dataclass, field

from app.application.casos_de_uso.pedidos.consultar_pedido import ConsultarPedido
from app.application.portas.pedidos import PedidoAcompanhadoRepository
from app.application.portas.relogio import Relogio
from app.domain.pedido import AndamentoDoPedido, PedidoAcompanhado, exigir_espaco_para_acompanhar
from app.domain.protocolo import exigir_protocolo
from app.domain.usuario import Usuario


@dataclass(frozen=True)
class PedidoComAndamento:
    pedido: PedidoAcompanhado
    andamentos: list[AndamentoDoPedido] = field(default_factory=list)


@dataclass(frozen=True)
class ServicosDePedidos:
    consultar: ConsultarPedido
    acompanhados: PedidoAcompanhadoRepository
    relogio: Relogio


@dataclass(frozen=True)
class ListarMeusPedidos:
    servicos: ServicosDePedidos

    def executar(self, cidadao: Usuario) -> list[PedidoComAndamento]:
        return [
            PedidoComAndamento(pedido, self.servicos.consultar.executar(pedido.protocolo))
            for pedido in self.servicos.acompanhados.listar(cidadao.id)
        ]


@dataclass(frozen=True)
class AcompanharPedido:
    """Guarda o protocolo mesmo sem registro na base: a fonte pode publicá-lo depois."""

    servicos: ServicosDePedidos

    def executar(self, cidadao: Usuario, protocolo_digitado: str) -> PedidoComAndamento:
        protocolo = exigir_protocolo(protocolo_digitado)
        guardados = self.servicos.acompanhados.listar(cidadao.id)
        pedido = next((item for item in guardados if item.protocolo == protocolo), None)
        if pedido is None:
            exigir_espaco_para_acompanhar(len(guardados))
            agora = self.servicos.relogio.agora()
            pedido = self.servicos.acompanhados.adicionar(cidadao.id, protocolo, agora)
        return PedidoComAndamento(pedido, self.servicos.consultar.executar(protocolo))


@dataclass(frozen=True)
class DeixarDeAcompanhar:
    servicos: ServicosDePedidos

    def executar(self, cidadao: Usuario, pedido_id: int) -> None:
        self.servicos.acompanhados.remover(cidadao.id, pedido_id)
