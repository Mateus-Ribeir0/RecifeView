import { createContext, useContext } from 'react'

import type { Filtros } from '../../domain/filtros'

export interface ContextoDosFiltrosValor {
  filtros: Filtros
  alterar: (mudanca: Partial<Filtros>) => void
  limpar: () => void
}

export const ContextoDosFiltros = createContext<ContextoDosFiltrosValor | null>(null)

export function useFiltrosGlobais(): ContextoDosFiltrosValor {
  const contexto = useContext(ContextoDosFiltros)
  if (!contexto) throw new Error('useFiltrosGlobais precisa de ProvedorDeFiltros')
  return contexto
}
