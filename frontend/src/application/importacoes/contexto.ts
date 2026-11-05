import { createContext, useContext } from 'react'

import type { ServicoDeImportacoes } from './servico'

export const ContextoDasImportacoes = createContext<ServicoDeImportacoes | null>(null)

export function useServicoDeImportacoes(): ServicoDeImportacoes {
  const servico = useContext(ContextoDasImportacoes)
  if (!servico) throw new Error('useServicoDeImportacoes precisa de ContextoDasImportacoes')
  return servico
}
