import type { CaixaDeNotificacoes } from '../../domain/notificacoes'

export interface ServicoDeNotificacoes {
  caixa(): Promise<CaixaDeNotificacoes>
  marcarComoLida(id: number): Promise<void>
  marcarTodasComoLidas(): Promise<void>
}
