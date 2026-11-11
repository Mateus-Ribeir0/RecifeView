import type { ServicoDeInformacao } from '../../application/informacao/servico'
import type { IndicadoresDoBairro } from '../../domain/cidade'
import type { AndamentoDoPedido, PedidoAcompanhado } from '../../domain/pedidos'
import type { ClienteHttp, Requisicao } from './cliente'
import { converterChaves } from './conversao'

export function criarServicoDeInformacao(cliente: ClienteHttp): ServicoDeInformacao {
  async function enviar<T>(caminho: string, requisicao: Requisicao = {}): Promise<T> {
    return converterChaves<T>(await cliente.enviar<unknown>(caminho, requisicao))
  }

  return {
    consultarPedido: (protocolo) =>
      enviar<AndamentoDoPedido[]>('/publico/pedidos/consultar', {
        metodo: 'POST',
        corpo: { protocolo },
      }),
    indicadoresDoBairro: (bairro) =>
      enviar<IndicadoresDoBairro>(`/publico/bairros/${encodeURIComponent(bairro)}`),
    meusPedidos: () => enviar<PedidoAcompanhado[]>('/cidade/pedidos', { autenticada: true }),
    acompanharPedido: (protocolo) =>
      enviar<PedidoAcompanhado>('/cidade/pedidos', {
        metodo: 'POST',
        corpo: { protocolo },
        autenticada: true,
      }),
    deixarDeAcompanhar: async (id) => {
      await cliente.enviar<unknown>(`/cidade/pedidos/${id}`, {
        metodo: 'DELETE',
        autenticada: true,
      })
    },
  }
}
