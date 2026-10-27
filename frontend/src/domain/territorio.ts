export type NumeroDaRpa = 1 | 2 | 3 | 4 | 5 | 6

export interface Rpa {
  numero: NumeroDaRpa
  nome: string
}

export const RPAS: readonly Rpa[] = [
  { numero: 1, nome: 'Centro' },
  { numero: 2, nome: 'Norte' },
  { numero: 3, nome: 'Noroeste' },
  { numero: 4, nome: 'Oeste' },
  { numero: 5, nome: 'Sudoeste' },
  { numero: 6, nome: 'Sul' },
]

export type Coordenada = readonly [longitude: number, latitude: number]
export type Anel = readonly Coordenada[]
export type Poligono = readonly Anel[]

export interface Bairro {
  codigo: number
  nome: string
  rpa: NumeroDaRpa
  poligonos: readonly Poligono[]
}
