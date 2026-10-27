import type { Anel, Bairro, Coordenada } from '../../domain/territorio'

const GRAUS_PARA_RADIANOS = Math.PI / 180

export interface BairroDesenhado {
  bairro: Bairro
  caminho: string
}

export interface MapaProjetado {
  largura: number
  altura: number
  bairros: BairroDesenhado[]
}

export function projetarBairros(bairros: readonly Bairro[], largura: number): MapaProjetado {
  const coordenadas = bairros.flatMap((bairro) => bairro.poligonos.flat(2))
  const longitudes = coordenadas.map(([longitude]) => longitude)
  const latitudes = coordenadas.map(([, latitude]) => latitude)
  const oeste = Math.min(...longitudes)
  const leste = Math.max(...longitudes)
  const sul = Math.min(...latitudes)
  const norte = Math.max(...latitudes)
  const fatorDaLongitude = Math.cos(((norte + sul) / 2) * GRAUS_PARA_RADIANOS)
  const escala = largura / ((leste - oeste) * fatorDaLongitude)

  const projetar = ([longitude, latitude]: Coordenada) =>
    `${((longitude - oeste) * fatorDaLongitude * escala).toFixed(1)},${((norte - latitude) * escala).toFixed(1)}`
  const desenharAnel = (anel: Anel) => `M${anel.map(projetar).join('L')}Z`

  return {
    largura,
    altura: Math.ceil((norte - sul) * escala),
    bairros: bairros.map((bairro) => ({
      bairro,
      caminho: bairro.poligonos.flat().map(desenharAnel).join(''),
    })),
  }
}
