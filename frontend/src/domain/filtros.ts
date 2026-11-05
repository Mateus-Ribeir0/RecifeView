const ANO_INICIAL_PADRAO = 2021
const ANO_FINAL_PADRAO = 2025

export interface Filtros {
  anoInicio: number
  anoFim: number
  rpas: readonly string[]
  bairros: readonly string[]
  categorias: readonly string[]
}

export const FILTROS_PADRAO: Filtros = {
  anoInicio: ANO_INICIAL_PADRAO,
  anoFim: ANO_FINAL_PADRAO,
  rpas: [],
  bairros: [],
  categorias: [],
}

export function temTerritorio(filtros: Filtros): boolean {
  return filtros.rpas.length > 0 || filtros.bairros.length > 0
}

export function estaNoPadrao(filtros: Filtros): boolean {
  return (
    filtros.anoInicio === ANO_INICIAL_PADRAO &&
    filtros.anoFim === ANO_FINAL_PADRAO &&
    !temTerritorio(filtros) &&
    filtros.categorias.length === 0
  )
}
