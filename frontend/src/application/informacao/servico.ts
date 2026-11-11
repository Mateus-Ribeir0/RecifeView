import type { IndicadoresDoBairro } from '../../domain/cidade'
import type { AndamentoDoPedido, PedidoAcompanhado } from '../../domain/pedidos'

export interface ServicoDeInformacao {
  consultarPedido(protocolo: string): Promise<readonly AndamentoDoPedido[]>
  indicadoresDoBairro(bairro: string): Promise<IndicadoresDoBairro>
  meusPedidos(): Promise<readonly PedidoAcompanhado[]>
  acompanharPedido(protocolo: string): Promise<PedidoAcompanhado>
  deixarDeAcompanhar(id: number): Promise<void>
}
