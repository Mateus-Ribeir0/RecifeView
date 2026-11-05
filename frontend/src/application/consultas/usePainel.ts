import { useCallback } from 'react'

import type { Filtros } from '../../domain/filtros'
import type { FonteDaFila, Julgamento } from '../../domain/prioridade'
import { useContextoDoPainel } from './contexto'
import { useConsulta } from './useConsulta'

export function useCatalogo() {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.catalogo(), [servico])
  return useConsulta('catalogo', null, buscar)
}

export function useVisaoGeral(filtros: Filtros) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.visaoGeral(filtros), [servico, filtros])
  return useConsulta('visao-geral', filtros, buscar)
}

export function useRetorno(filtros: Filtros) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.retorno(filtros), [servico, filtros])
  return useConsulta('retorno', filtros, buscar)
}

export function useOuvidoria(filtros: Filtros) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.ouvidoria(filtros), [servico, filtros])
  return useConsulta('ouvidoria', { inicio: filtros.anoInicio, fim: filtros.anoFim }, buscar)
}

export function useRecorrencias(filtros: Filtros, semGenerico: boolean) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(
    () => servico.recorrencias(filtros, semGenerico),
    [servico, filtros, semGenerico],
  )
  return useConsulta('recorrencias', { filtros, semGenerico }, buscar)
}

export function usePrazos(filtros: Filtros, semMesmoDia: boolean) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(
    () => servico.prazos(filtros, semMesmoDia),
    [servico, filtros, semMesmoDia],
  )
  return useConsulta('prazos', { filtros, semMesmoDia }, buscar)
}

export function useTerritorio(filtros: Filtros) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.territorio(filtros), [servico, filtros])
  return useConsulta('territorio', filtros, buscar)
}

export function useCriterios() {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.criterios(), [servico])
  return useConsulta('criterios', null, buscar)
}

export function usePrioridade(julgamentos: readonly Julgamento[]) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.prioridade(julgamentos), [servico, julgamentos])
  return useConsulta('prioridade', julgamentos, buscar)
}

interface ParametrosDaFila {
  fonte: FonteDaFila
  julgamentos: readonly Julgamento[]
  semente: number
  filtros: Filtros
}

export function useFila(parametros: ParametrosDaFila) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.fila(parametros), [servico, parametros])
  return useConsulta('fila', parametros, buscar)
}

export function useCalendarioDaWarRoom() {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.calendario(), [servico])
  return useConsulta('calendario', null, buscar)
}

export function useQuadroDoDia(dia: string | null, inicioDaSerie: string | null) {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(
    () => (dia ? servico.quadroDoDia(dia, inicioDaSerie) : Promise.reject(new Error('sem dia'))),
    [servico, dia, inicioDaSerie],
  )
  return useConsulta('quadro', { dia, inicioDaSerie }, buscar)
}

export function useSobreOsDados() {
  const { servico } = useContextoDoPainel()
  const buscar = useCallback(() => servico.sobre(), [servico])
  return useConsulta('sobre', null, buscar)
}
