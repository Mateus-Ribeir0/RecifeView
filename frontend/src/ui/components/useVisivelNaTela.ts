import { useEffect, useRef, useState, type RefObject } from 'react'

const MARGEM_ANTES_DA_BORDA = '0px 0px -8% 0px'

function observadorDisponivel(): boolean {
  return typeof IntersectionObserver === 'function'
}

export function useVisivelNaTela<T extends Element>(): [RefObject<T | null>, boolean] {
  const referencia = useRef<T>(null)
  const [visivel, definirVisivel] = useState(() => !observadorDisponivel())

  useEffect(() => {
    const elemento = referencia.current
    if (!elemento || !observadorDisponivel()) return
    const observador = new IntersectionObserver(
      ([entrada]) => {
        if (!entrada?.isIntersecting) return
        definirVisivel(true)
        observador.disconnect()
      },
      { rootMargin: MARGEM_ANTES_DA_BORDA },
    )
    observador.observe(elemento)
    return () => observador.disconnect()
  }, [])

  return [referencia, visivel]
}
