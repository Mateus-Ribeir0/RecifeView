import type { ServicoDeNotificacoes } from '../../application/notificacoes/servico'
import type { CaixaDeNotificacoes } from '../../domain/notificacoes'
import type { ClienteHttp } from './cliente'
import { converterChaves } from './conversao'

const BASE = '/notificacoes'

export function criarServicoDeNotificacoes(cliente: ClienteHttp): ServicoDeNotificacoes {
  return {
    async caixa() {
      const resposta = await cliente.enviar<unknown>(BASE, { autenticada: true })
      return converterChaves<CaixaDeNotificacoes>(resposta)
    },
    async marcarComoLida(id) {
      await cliente.enviar<unknown>(`${BASE}/${id}/leitura`, { metodo: 'POST', autenticada: true })
    },
    async marcarTodasComoLidas() {
      await cliente.enviar<unknown>(`${BASE}/leitura`, { metodo: 'POST', autenticada: true })
    },
  }
}
