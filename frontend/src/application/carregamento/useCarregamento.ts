import { useCallback, useEffect, useState } from 'react'

export interface Carregamento<T> {
  dados: T | null
  erro: unknown
  carregando: boolean
  recarregar: () => void
}

interface Guardado<T> {
  chave: string | null
  dados: T | null
  erro: unknown
}

/** Carrega sob demanda e recarrega depois de uma ação, sem o cache do painel. */
export function useCarregamento<T>(
  chave: string,
  buscar: (() => Promise<T>) | null,
): Carregamento<T> {
  const [guardado, definirGuardado] = useState<Guardado<T>>({
    chave: null,
    dados: null,
    erro: null,
  })
  const [versao, definirVersao] = useState(0)
  const recarregar = useCallback(() => definirVersao((atual) => atual + 1), [])
  const chaveCompleta = `${chave}#${versao}`

  useEffect(() => {
    if (!buscar) return
    let ativo = true
    buscar().then(
      (dados) => {
        if (ativo) definirGuardado({ chave: chaveCompleta, dados, erro: null })
      },
      (erro: unknown) => {
        if (ativo) definirGuardado((atual) => ({ ...atual, chave: chaveCompleta, erro }))
      },
    )
    return () => {
      ativo = false
    }
  }, [chaveCompleta, buscar])

  if (!buscar) return { dados: null, erro: null, carregando: false, recarregar }
  const carregando = guardado.chave !== chaveCompleta
  return { dados: guardado.dados, erro: carregando ? null : guardado.erro, carregando, recarregar }
}
