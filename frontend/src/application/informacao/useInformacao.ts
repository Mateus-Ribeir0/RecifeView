import { useCallback } from 'react'

import type { IndicadoresDoBairro } from '../../domain/cidade'
import type { PedidoAcompanhado } from '../../domain/pedidos'
import { useCarregamento, type Carregamento } from '../carregamento/useCarregamento'
import { useServicoDeInformacao } from './contexto'

export function useIndicadoresDoBairro(bairro: string): Carregamento<IndicadoresDoBairro> {
  const servico = useServicoDeInformacao()
  const buscar = useCallback(() => servico.indicadoresDoBairro(bairro), [servico, bairro])
  return useCarregamento(bairro, bairro ? buscar : null)
}

export function useMeusPedidos(): Carregamento<readonly PedidoAcompanhado[]> {
  const servico = useServicoDeInformacao()
  const buscar = useCallback(() => servico.meusPedidos(), [servico])
  return useCarregamento('meus-pedidos', buscar)
}
