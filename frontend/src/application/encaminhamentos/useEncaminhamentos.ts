import { useCallback } from 'react'

import type {
  Encaminhamento,
  EncaminhamentoParaOOrgao,
  FiltroDeEncaminhamentos,
  OrgaoDoCatalogo,
  PreparoDoEncaminhamento,
  QuadroDeEncaminhamentos,
} from '../../domain/encaminhamentos'
import { useCarregamento, type Carregamento } from '../carregamento/useCarregamento'
import { useServicoDeEncaminhamentos, useServicoDeRetornoDoOrgao } from './contexto'

export function useQuadroDeEncaminhamentos(
  filtro: FiltroDeEncaminhamentos,
): Carregamento<QuadroDeEncaminhamentos> {
  const servico = useServicoDeEncaminhamentos()
  const { situacao, orgao, soAtrasados, deslocamento } = filtro
  const buscar = useCallback(
    () => servico.listar({ situacao, orgao, soAtrasados, deslocamento }),
    [servico, situacao, orgao, soAtrasados, deslocamento],
  )
  return useCarregamento(JSON.stringify(filtro), buscar)
}

export function useEncaminhamento(id: number): Carregamento<Encaminhamento> {
  const servico = useServicoDeEncaminhamentos()
  const buscar = useCallback(() => servico.consultar(id), [servico, id])
  return useCarregamento(String(id), buscar)
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
