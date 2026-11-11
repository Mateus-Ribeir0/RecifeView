import { createContext, useContext } from 'react'

import type { ServicoDeEncaminhamentos, ServicoDeRetornoDoOrgao } from './servico'

export const ContextoDosEncaminhamentos = createContext<ServicoDeEncaminhamentos | null>(null)
export const ContextoDoRetornoDoOrgao = createContext<ServicoDeRetornoDoOrgao | null>(null)

export function useServicoDeEncaminhamentos(): ServicoDeEncaminhamentos {
  const servico = useContext(ContextoDosEncaminhamentos)
  if (!servico) throw new Error('useServicoDeEncaminhamentos precisa de ContextoDosEncaminhamentos')
  return servico
}

export function useServicoDeRetornoDoOrgao(): ServicoDeRetornoDoOrgao {
  const servico = useContext(ContextoDoRetornoDoOrgao)
  if (!servico) throw new Error('useServicoDeRetornoDoOrgao precisa de ContextoDoRetornoDoOrgao')
  return servico
}
