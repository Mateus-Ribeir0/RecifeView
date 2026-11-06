import { createContext, useContext } from 'react'

import type { ServicoDeContribuicoes } from './servico'

export const ContextoDasContribuicoes = createContext<ServicoDeContribuicoes | null>(null)

export function useServicoDeContribuicoes(): ServicoDeContribuicoes {
  const servico = useContext(ContextoDasContribuicoes)
  if (!servico) throw new Error('useServicoDeContribuicoes precisa de ContextoDasContribuicoes')
  return servico
}
