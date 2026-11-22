import { useEffect } from 'react'

export const EVENTO_DE_NOVIDADE = 'recifeview:novidade'

export function avisarQueChegouNovidade(): void {
  window.dispatchEvent(new Event(EVENTO_DE_NOVIDADE))
}

/** A tela do ciclo se recarrega sozinha quando o sino recebe uma notificação nova. */
export function useAtualizacaoAutomatica(recarregar: () => void): void {
  useEffect(() => {
    window.addEventListener(EVENTO_DE_NOVIDADE, recarregar)
    return () => window.removeEventListener(EVENTO_DE_NOVIDADE, recarregar)
  }, [recarregar])
}
