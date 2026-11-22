import { createContext, useContext } from 'react'

import type { ServicoDoOrgao } from './servico'

export const ContextoDoOrgao = createContext<ServicoDoOrgao | null>(null)

export function useServicoDoOrgao(): ServicoDoOrgao {
  const servico = useContext(ContextoDoOrgao)
  if (!servico) throw new Error('useServicoDoOrgao precisa de ContextoDoOrgao')
  return servico
}
