import { useCallback, useEffect, useSyncExternalStore } from 'react'

import { useContextoDoPainel } from './contexto'

export interface ResultadoDaConsulta<T> {
  dados: T | undefined
  carregando: boolean
  atualizando: boolean
  erro: unknown
  tentarDeNovo: () => void
}

/** Mantém os dados anteriores na tela enquanto os novos chegam, para o gráfico não piscar. */
export function useConsulta<T>(
  grupo: string,
  parametros: unknown,
  buscar: () => Promise<T>,
): ResultadoDaConsulta<T> {
  const { cache } = useContextoDoPainel()
  const chave = `${grupo}:${JSON.stringify(parametros)}`
  const entrada = useSyncExternalStore(cache.assinar, () => cache.ler<T>(chave))

  useEffect(() => {
    cache.garantir(grupo, chave, buscar)
  }, [cache, grupo, chave, buscar])

  const tentarDeNovo = useCallback(
    () => cache.recarregar(grupo, chave, buscar),
    [cache, grupo, chave, buscar],
  )

  if (entrada?.situacao === 'pronta') {
    return { dados: entrada.dados, carregando: false, atualizando: false, erro: null, tentarDeNovo }
  }
  if (entrada?.situacao === 'erro') {
    return {
      dados: undefined,
      carregando: false,
      atualizando: false,
      erro: entrada.erro,
      tentarDeNovo,
    }
  }
  const anteriores = cache.ultimaPronta<T>(grupo)
  return {
    dados: anteriores,
    carregando: anteriores === undefined,
    atualizando: anteriores !== undefined,
    erro: null,
    tentarDeNovo,
  }
}
