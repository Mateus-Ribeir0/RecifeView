import { useCallback } from 'react'

import type {
  DemandaDoOrgao,
  FilaDoOrgao,
  OcorrenciaDoOrgao,
  PainelDoOrgao,
  PedidoDaFila,
} from '../../domain/corporativo'
import { useCarregamento, type Carregamento } from '../carregamento/useCarregamento'
import { useAtualizacaoAutomatica } from '../notificacoes/useAtualizacaoAutomatica'
import { useServicoDoOrgao } from './contexto'
import type { PeriodoDosDados } from './servico'

export function usePainelDoOrgao(): Carregamento<PainelDoOrgao> {
  const servico = useServicoDoOrgao()
  const buscar = useCallback(() => servico.painel(), [servico])
  const carregamento = useCarregamento('painel-do-orgao', buscar)
  useAtualizacaoAutomatica(carregamento.recarregar)
  return carregamento
}

export function useFilaDoOrgao(pedido: PedidoDaFila): Carregamento<FilaDoOrgao> {
  const servico = useServicoDoOrgao()
  const { aba, bairro, categoria, deslocamento } = pedido
  const buscar = useCallback(
    () => servico.fila({ aba, bairro, categoria, deslocamento }),
    [servico, aba, bairro, categoria, deslocamento],
  )
  const carregamento = useCarregamento(JSON.stringify(pedido), buscar)
  useAtualizacaoAutomatica(carregamento.recarregar)
  return carregamento
}

export function useOcorrenciaDoOrgao(id: number): Carregamento<OcorrenciaDoOrgao> {
  const servico = useServicoDoOrgao()
  const buscar = useCallback(() => servico.ocorrencia(id), [servico, id])
  return useCarregamento(`ocorrencia-${id}`, buscar)
}

export function useDemandaDoOrgao(periodo: PeriodoDosDados): Carregamento<DemandaDoOrgao> {
  const servico = useServicoDoOrgao()
  const { anoInicio, anoFim } = periodo
  const buscar = useCallback(
    () => servico.dados({ anoInicio, anoFim }),
    [servico, anoInicio, anoFim],
  )
  return useCarregamento(`dados-${anoInicio}-${anoFim}`, buscar)
}
