import { useCallback } from 'react'

import type {
  DesempenhoDosOrgaos,
  DetalheDoEncaminhamento,
  EncaminhamentoParaOOrgao,
  FiltroDeEncaminhamentos,
  OrgaoDoCatalogo,
  PendenciasDoPainel,
  PreparoDoEncaminhamento,
  QuadroDeEncaminhamentos,
} from '../../domain/encaminhamentos'
import { useCarregamento, type Carregamento } from '../carregamento/useCarregamento'
import { useAtualizacaoAutomatica } from '../notificacoes/useAtualizacaoAutomatica'
import { useServicoDeEncaminhamentos, useServicoDeRetornoDoOrgao } from './contexto'

export function useQuadroDeEncaminhamentos(
  filtro: FiltroDeEncaminhamentos,
): Carregamento<QuadroDeEncaminhamentos> {
  const servico = useServicoDeEncaminhamentos()
  const { situacao, orgao, soAtrasados, pedemAcao, deslocamento } = filtro
  const buscar = useCallback(
    () => servico.listar({ situacao, orgao, soAtrasados, pedemAcao, deslocamento }),
    [servico, situacao, orgao, soAtrasados, pedemAcao, deslocamento],
  )
  const carregamento = useCarregamento(JSON.stringify(filtro), buscar)
  useAtualizacaoAutomatica(carregamento.recarregar)
  return carregamento
}

export function useEncaminhamento(id: number): Carregamento<DetalheDoEncaminhamento> {
  const servico = useServicoDeEncaminhamentos()
  const buscar = useCallback(() => servico.consultar(id), [servico, id])
  const carregamento = useCarregamento(String(id), buscar)
  useAtualizacaoAutomatica(carregamento.recarregar)
  return carregamento
}

export function usePreparoDoEncaminhamento(
  chaveRegistro: string | null,
): Carregamento<PreparoDoEncaminhamento> {
  const servico = useServicoDeEncaminhamentos()
  const buscar = useCallback(() => servico.preparar(chaveRegistro ?? ''), [servico, chaveRegistro])
  return useCarregamento(chaveRegistro ?? '', chaveRegistro ? buscar : null)
}

export function useEncaminhamentoPeloLink(token: string): Carregamento<EncaminhamentoParaOOrgao> {
  const servico = useServicoDeRetornoDoOrgao()
  const buscar = useCallback(() => servico.abrir(token), [servico, token])
  return useCarregamento(token, buscar)
}

export function useOrgaos(): Carregamento<readonly OrgaoDoCatalogo[]> {
  const servico = useServicoDeEncaminhamentos()
  const buscar = useCallback(() => servico.orgaos(), [servico])
  return useCarregamento('orgaos', buscar)
}

/** Recarrega a cada troca de tela: o contador do menu acompanha o que a gestão acabou de fazer. */
export function usePendenciasDoPainel(rota: string): Carregamento<PendenciasDoPainel> {
  const servico = useServicoDeEncaminhamentos()
  const buscar = useCallback(() => servico.pendencias(), [servico])
  const carregamento = useCarregamento(`pendencias:${rota}`, buscar)
  useAtualizacaoAutomatica(carregamento.recarregar)
  return carregamento
}

export function useDesempenhoDosOrgaos(): Carregamento<DesempenhoDosOrgaos> {
  const servico = useServicoDeEncaminhamentos()
  const buscar = useCallback(() => servico.desempenho(), [servico])
  const carregamento = useCarregamento('desempenho', buscar)
  useAtualizacaoAutomatica(carregamento.recarregar)
  return carregamento
}
