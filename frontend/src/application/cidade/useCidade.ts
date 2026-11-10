import { useCallback, useEffect, useState } from 'react'

import type { FiltroDaCidade, IndicadoresDoBairro, OcorrenciaDaCidade } from '../../domain/cidade'
import { useServicoDaCidade } from './contexto'

interface Resultado<T> {
  dados: T | null
  erro: unknown
  carregando: boolean
}

interface Guardado<T> {
  chave: string | null
  dados: T | null
  erro: unknown
}

function useConsultaDaCidade<T>(chave: string, buscar: (() => Promise<T>) | null): Resultado<T> {
  const [guardado, definirGuardado] = useState<Guardado<T>>({
    chave: null,
    dados: null,
    erro: null,
  })

  useEffect(() => {
    if (!buscar) return
    let ativo = true
    buscar().then(
      (dados) => {
        if (ativo) definirGuardado({ chave, dados, erro: null })
      },
      (erro: unknown) => {
        if (ativo) definirGuardado({ chave, dados: null, erro })
      },
    )
    return () => {
      ativo = false
    }
  }, [chave, buscar])

  if (!buscar) return { dados: null, erro: null, carregando: false }
  const carregando = guardado.chave !== chave
  return { dados: guardado.dados, erro: carregando ? null : guardado.erro, carregando }
}

export function useOcorrenciasDaCidade(
  filtro: FiltroDaCidade,
): Resultado<readonly OcorrenciaDaCidade[]> {
  const servico = useServicoDaCidade()
  const { bairro, tema } = filtro
  const buscar = useCallback(() => servico.ocorrencias({ bairro, tema }), [servico, bairro, tema])
  return useConsultaDaCidade(`${bairro}|${tema}`, buscar)
}

export function useMeuBairro(bairro: string): Resultado<IndicadoresDoBairro> {
  const servico = useServicoDaCidade()
  const buscar = useCallback(() => servico.meuBairro(bairro), [servico, bairro])
  return useConsultaDaCidade(bairro, bairro ? buscar : null)
}
