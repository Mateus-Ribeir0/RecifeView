import type { Bairro, NumeroDaRpa, Poligono } from '../../domain/territorio'

interface FeicaoDaMalha {
  properties: { codigo: number; nome: string; rpa: number }
  geometry: { coordinates: unknown }
}

let carregamento: Promise<readonly Bairro[]> | null = null

function paraBairro({ properties, geometry }: FeicaoDaMalha): Bairro {
  return {
    codigo: properties.codigo,
    nome: properties.nome,
    rpa: properties.rpa as NumeroDaRpa,
    poligonos: geometry.coordinates as readonly Poligono[],
  }
}

export function carregarBairros(): Promise<readonly Bairro[]> {
  carregamento ??= import('./dados/bairros-recife.json').then((modulo) =>
    (modulo.default.features as FeicaoDaMalha[]).map(paraBairro),
  )
  return carregamento
}

export interface FeicaoDeBairro {
  type: 'Feature'
  properties: { codigo: number; nome: string; rpa: number }
  geometry: { type: string; coordinates: unknown }
}

export interface MalhaDosBairros {
  type: 'FeatureCollection'
  features: FeicaoDeBairro[]
}

export async function carregarMalha(): Promise<MalhaDosBairros> {
  const modulo = await import('./dados/bairros-recife.json')
  return { type: 'FeatureCollection', features: modulo.default.features as FeicaoDeBairro[] }
}
