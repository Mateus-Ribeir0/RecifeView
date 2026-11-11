import { createContext, useContext } from 'react'

import type { ServicoDeInformacao } from './servico'

export const ContextoDaInformacao = createContext<ServicoDeInformacao | null>(null)

export function useServicoDeInformacao(): ServicoDeInformacao {
  const servico = useContext(ContextoDaInformacao)
  if (!servico) throw new Error('useServicoDeInformacao precisa de ContextoDaInformacao')
  return servico
}
