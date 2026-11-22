import { createContext, useContext } from 'react'

import type { ServicoDeNotificacoes } from './servico'

export const ContextoDasNotificacoes = createContext<ServicoDeNotificacoes | null>(null)

export function useServicoDeNotificacoes(): ServicoDeNotificacoes {
  const servico = useContext(ContextoDasNotificacoes)
  if (!servico) throw new Error('useServicoDeNotificacoes precisa de ContextoDasNotificacoes')
  return servico
}
