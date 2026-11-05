import { useCallback, useEffect, useState } from 'react'

import { estaEmProcessamento, type DetalheDaImportacao } from '../../domain/importacoes'
import { useContextoDoPainel } from '../consultas/contexto'
import { useServicoDeImportacoes } from './contexto'

const INTERVALO_DE_ATUALIZACAO_EM_MS = 1500

interface EstadoDaImportacao {
  importacao: DetalheDaImportacao | null
  erro: unknown
}

export interface ImportacaoAcompanhada extends EstadoDaImportacao {
  recarregar: () => void
}

/** Acompanha uma importação e, quando ela termina, esquece as consultas antigas do painel. */
export function useImportacao(id: number): ImportacaoAcompanhada {
  const servico = useServicoDeImportacoes()
  const { cache } = useContextoDoPainel()
  const [estado, definirEstado] = useState<EstadoDaImportacao>({ importacao: null, erro: null })
  const [versao, definirVersao] = useState(0)
  const recarregar = useCallback(() => definirVersao((atual) => atual + 1), [])

  useEffect(() => {
    let ativo = true
    let temporizador: ReturnType<typeof setTimeout> | undefined
    let processava = false

    async function atualizar() {
      try {
        const importacao = await servico.consultar(id)
        if (!ativo) return
        definirEstado({ importacao, erro: null })
        const processando = estaEmProcessamento(importacao.status)
        if (processava && !processando) cache.esquecerTudo()
        processava = processando
        if (processando) temporizador = setTimeout(atualizar, INTERVALO_DE_ATUALIZACAO_EM_MS)
      } catch (erro) {
        if (ativo) definirEstado((atual) => ({ ...atual, erro }))
      }
    }

    void atualizar()
    return () => {
      ativo = false
      clearTimeout(temporizador)
    }
  }, [servico, cache, id, versao])

  return { ...estado, recarregar }
}
