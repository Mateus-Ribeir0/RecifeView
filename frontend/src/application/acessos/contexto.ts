import { createContext, useCallback, useContext } from 'react'

import type { ListaDeAcessos } from '../../domain/acessos'
import { useCarregamento, type Carregamento } from '../carregamento/useCarregamento'
import type { ServicoDeAcessos } from './servico'

export const ContextoDosAcessos = createContext<ServicoDeAcessos | null>(null)

export function useServicoDeAcessos(): ServicoDeAcessos {
  const servico = useContext(ContextoDosAcessos)
  if (!servico) throw new Error('useServicoDeAcessos precisa de ContextoDosAcessos')
  return servico
}

export function useAcessosCorporativos(): Carregamento<ListaDeAcessos> {
  const servico = useServicoDeAcessos()
  const buscar = useCallback(() => servico.listar(), [servico])
  return useCarregamento('acessos-corporativos', buscar)
}
