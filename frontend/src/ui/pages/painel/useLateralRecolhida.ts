import { useCallback, useState } from 'react'

const CHAVE_DA_PREFERENCIA = 'recifeview.lateral-recolhida'

function lerPreferencia(): boolean {
  return window.localStorage.getItem(CHAVE_DA_PREFERENCIA) === 'sim'
}

export function useLateralRecolhida(): [boolean, () => void] {
  const [recolhida, definirRecolhida] = useState(lerPreferencia)
  const alternar = useCallback(() => {
    definirRecolhida((atual) => {
      window.localStorage.setItem(CHAVE_DA_PREFERENCIA, atual ? 'nao' : 'sim')
      return !atual
    })
  }, [])
  return [recolhida, alternar]
}
