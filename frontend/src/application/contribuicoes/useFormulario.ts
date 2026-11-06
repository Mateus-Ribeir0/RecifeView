import { useEffect, useState } from 'react'

import type { CatalogoDoFormulario } from '../../domain/contribuicoes'
import { useServicoDeContribuicoes } from './contexto'

interface EstadoDoCatalogo {
  catalogo: CatalogoDoFormulario | null
  erro: unknown
}

export function useCatalogoDoFormulario(): EstadoDoCatalogo {
  const servico = useServicoDeContribuicoes()
  const [estado, definirEstado] = useState<EstadoDoCatalogo>({ catalogo: null, erro: null })

  useEffect(() => {
    let ativo = true
    servico.catalogo().then(
      (catalogo) => {
        if (ativo) definirEstado({ catalogo, erro: null })
      },
      (erro: unknown) => {
        if (ativo) definirEstado({ catalogo: null, erro })
      },
    )
    return () => {
      ativo = false
    }
  }, [servico])

  return estado
}

export function useLogradourosDoBairro(bairro: string): readonly string[] {
  const servico = useServicoDeContribuicoes()
  const [vias, definirVias] = useState<readonly string[]>([])

  useEffect(() => {
    if (!bairro) return
    let ativo = true
    servico.logradouros(bairro).then(
      (lista) => {
        if (ativo) definirVias(lista)
      },
      () => {
        if (ativo) definirVias([])
      },
    )
    return () => {
      ativo = false
    }
  }, [servico, bairro])

  return bairro ? vias : []
}
