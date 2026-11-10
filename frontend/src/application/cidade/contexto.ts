import { createContext, useContext } from 'react'

import type { ServicoDaCidade } from './servico'

export const ContextoDaCidade = createContext<ServicoDaCidade | null>(null)

export function useServicoDaCidade(): ServicoDaCidade {
  const servico = useContext(ContextoDaCidade)
  if (!servico) throw new Error('useServicoDaCidade precisa de ContextoDaCidade')
  return servico
}
