import { useEffect, useState } from 'react'

/** Só entrega o valor depois de ele parar de mudar: evita uma consulta por passo do controle. */
export function useValorAtrasado<T>(valor: T, atrasoEmMs: number): T {
  const [atrasado, definirAtrasado] = useState(valor)
  useEffect(() => {
    const temporizador = setTimeout(() => definirAtrasado(valor), atrasoEmMs)
    return () => clearTimeout(temporizador)
  }, [valor, atrasoEmMs])
  return atrasado
}
