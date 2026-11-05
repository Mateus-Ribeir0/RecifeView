import { formatarPeriodo } from './formatacao'
import { nomeDaCategoria } from './nomes'

const ANO_INICIAL_PADRAO = 2021
const ANO_FINAL_PADRAO = 2025
const BAIRROS_NO_RESUMO = 4
const CATEGORIAS_NO_RESUMO = 3

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

function resumirLista(nomes: readonly string[], limite: number): string {
  const visiveis = nomes.slice(0, limite).join(', ')
  return nomes.length > limite ? `${visiveis} e mais ${nomes.length - limite}` : visiveis
}

export function resumirRecorte(
  filtros: Filtros,
  nomeDoBairro: (bairro: string) => string = (bairro) => bairro,
): string {
  const partes = [formatarPeriodo(filtros.anoInicio, filtros.anoFim)]
  if (filtros.rpas.length) partes.push(`RPA ${filtros.rpas.join(', ')}`)
  if (filtros.bairros.length) {
    partes.push(resumirLista(filtros.bairros.map(nomeDoBairro), BAIRROS_NO_RESUMO))
  }
  if (filtros.categorias.length) {
    partes.push(resumirLista(filtros.categorias.map(nomeDaCategoria), CATEGORIAS_NO_RESUMO))
  }
  return partes.join(' · ')
}
