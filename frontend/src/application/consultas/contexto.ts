import { createContext, useContext } from 'react'

import type { CacheDeConsultas } from './cache'
import type { ServicoDoPainel } from './servico'

export interface ContextoDoPainelValor {
  servico: ServicoDoPainel
  cache: CacheDeConsultas
}

export const ContextoDoPainel = createContext<ContextoDoPainelValor | null>(null)

export function useContextoDoPainel(): ContextoDoPainelValor {
  const contexto = useContext(ContextoDoPainel)
  if (!contexto) throw new Error('useContextoDoPainel precisa de ProvedorDoPainel')
  return contexto
}
