from dataclasses import dataclass

from app.application.portas.pedidos import ConsultaDePedidos, HistoricoDeEncaminhamentos
from app.domain.pedido import AndamentoDoPedido
from app.domain.protocolo import exigir_protocolo


@dataclass(frozen=True)
class ConsultarPedido:
    consulta: ConsultaDePedidos
    encaminhamentos: HistoricoDeEncaminhamentos

    def executar(self, protocolo_digitado: str) -> list[AndamentoDoPedido]:
        protocolo = exigir_protocolo(protocolo_digitado)
        return [
            AndamentoDoPedido(
                registro, tuple(self.encaminhamentos.da_ocorrencia(registro.chave_registro))
            )
            for registro in self.consulta.registros(protocolo)
        ]
