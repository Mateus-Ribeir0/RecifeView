import { useCallback, useMemo, useState, type ReactNode } from 'react'

import { FILTROS_PADRAO, type Filtros } from '../../domain/filtros'
import { ContextoDosFiltros } from './contexto'

export function ProvedorDeFiltros({ children }: { children: ReactNode }) {
  const [filtros, definirFiltros] = useState<Filtros>(FILTROS_PADRAO)
  const alterar = useCallback(
    (mudanca: Partial<Filtros>) => definirFiltros((atuais) => ({ ...atuais, ...mudanca })),
    [],
  )
  const limpar = useCallback(() => definirFiltros(FILTROS_PADRAO), [])
  const valor = useMemo(() => ({ filtros, alterar, limpar }), [filtros, alterar, limpar])
  return <ContextoDosFiltros value={valor}>{children}</ContextoDosFiltros>
}
