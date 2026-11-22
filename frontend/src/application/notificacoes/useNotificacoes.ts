import { useCallback, useEffect, useRef, useState } from 'react'

import { CAIXA_VAZIA, chegouNovidade, type CaixaDeNotificacoes } from '../../domain/notificacoes'
import { useServicoDeNotificacoes } from './contexto'
import { avisarQueChegouNovidade } from './useAtualizacaoAutomatica'

export const INTERVALO_DA_CONSULTA_EM_MS = 30_000

export interface Notificacoes {
  caixa: CaixaDeNotificacoes
  indisponivel: boolean
  marcarComoLida: (id: number) => Promise<void>
  marcarTodasComoLidas: () => Promise<void>
}

/** Consulta a caixa a cada 30 segundos, com a aba visível, e ao voltar para a aba. */
export function useNotificacoes(): Notificacoes {
  const servico = useServicoDeNotificacoes()
  const [caixa, definirCaixa] = useState<CaixaDeNotificacoes>(CAIXA_VAZIA)
  const [indisponivel, definirIndisponivel] = useState(false)
  const anterior = useRef<CaixaDeNotificacoes | null>(null)

  const consultar = useCallback((): Promise<void> => {
    if (document.visibilityState === 'hidden') return Promise.resolve()
    return servico.caixa().then(
      (atual) => {
        if (anterior.current && chegouNovidade(anterior.current, atual)) avisarQueChegouNovidade()
        anterior.current = atual
        definirCaixa(atual)
        definirIndisponivel(false)
      },
      () => definirIndisponivel(true),
    )
  }, [servico])

  useEffect(() => {
    void consultar()
    const intervalo = window.setInterval(() => void consultar(), INTERVALO_DA_CONSULTA_EM_MS)
    const aoVoltar = () => void consultar()
    document.addEventListener('visibilitychange', aoVoltar)
    return () => {
      window.clearInterval(intervalo)
      document.removeEventListener('visibilitychange', aoVoltar)
    }
  }, [consultar])

  const marcarComoLida = useCallback(
    async (id: number) => {
      await servico.marcarComoLida(id)
      await consultar()
    },
    [servico, consultar],
  )

  const marcarTodasComoLidas = useCallback(async () => {
    await servico.marcarTodasComoLidas()
    await consultar()
  }, [servico, consultar])

  return { caixa, indisponivel, marcarComoLida, marcarTodasComoLidas }
}
