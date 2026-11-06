import { useCallback, useEffect, useState } from 'react'

import type {
  PaginaDeOcorrencias,
  ParParaRevisar,
  ResumoDasContribuicoes,
} from '../../domain/contribuicoes'
import { useServicoDeContribuicoes } from './contexto'

export interface FilaDeRelatos {
  resumo: ResumoDasContribuicoes
  pares: readonly ParParaRevisar[]
  ocorrencias: PaginaDeOcorrencias
}

interface EstadoDaFila {
  fila: FilaDeRelatos | null
  erro: unknown
}

export function useFilaDeRelatos(deslocamento: number): EstadoDaFila & { recarregar: () => void } {
  const servico = useServicoDeContribuicoes()
  const [estado, definirEstado] = useState<EstadoDaFila>({ fila: null, erro: null })
  const [versao, definirVersao] = useState(0)
  const recarregar = useCallback(() => definirVersao((atual) => atual + 1), [])

  useEffect(() => {
    let ativo = true
    Promise.all([servico.resumo(), servico.pares(), servico.ocorrencias(deslocamento)]).then(
      ([resumo, pares, ocorrencias]) => {
        if (ativo) definirEstado({ fila: { resumo, pares, ocorrencias }, erro: null })
      },
      (erro: unknown) => {
        if (ativo) definirEstado((atual) => ({ ...atual, erro }))
      },
    )
    return () => {
      ativo = false
    }
  }, [servico, deslocamento, versao])

  return { ...estado, recarregar }
}
