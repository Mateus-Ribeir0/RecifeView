import { use } from 'react'

import { ContextoDaSessao, type Sessao } from './contexto'

export function useSessao(): Sessao {
  const sessao = use(ContextoDaSessao)
  if (!sessao) throw new Error('useSessao precisa estar dentro de ProvedorDeSessao')
  return sessao
}
