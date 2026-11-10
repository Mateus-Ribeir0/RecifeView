import { useEffect, useState } from 'react'

const SEGUNDOS_ENTRE_ENVIOS = 60
const UM_SEGUNDO_EM_MS = 1000

export function useEsperaParaReenviar(): [number, () => void] {
  const [restante, definirRestante] = useState(SEGUNDOS_ENTRE_ENVIOS)

  useEffect(() => {
    if (restante <= 0) return
    const temporizador = setTimeout(() => definirRestante((atual) => atual - 1), UM_SEGUNDO_EM_MS)
    return () => clearTimeout(temporizador)
  }, [restante])

  return [restante, () => definirRestante(SEGUNDOS_ENTRE_ENVIOS)]
}
