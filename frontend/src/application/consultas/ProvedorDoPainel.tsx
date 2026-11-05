import { useState, type ReactNode } from 'react'

import { CacheDeConsultas } from './cache'
import { ContextoDoPainel } from './contexto'
import type { ServicoDoPainel } from './servico'

interface Propriedades {
  servico: ServicoDoPainel
  children: ReactNode
}

export function ProvedorDoPainel({ servico, children }: Propriedades) {
  const [cache] = useState(() => new CacheDeConsultas())
  return <ContextoDoPainel value={{ servico, cache }}>{children}</ContextoDoPainel>
}
