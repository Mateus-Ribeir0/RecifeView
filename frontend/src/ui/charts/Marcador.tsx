import { COR } from './estilo'

export type FormaDoMarcador = 'circulo' | 'quadrado' | 'triangulo' | 'losango' | 'cruz' | 'anel'

interface Propriedades {
  x?: number
  y?: number
  cor: string
  forma: FormaDoMarcador
  opacidade?: number
}

const TAMANHO = 5

function caminhoDaForma(forma: FormaDoMarcador): string {
  const t = TAMANHO
  if (forma === 'triangulo') return `M0,${-t - 1} L${t + 1},${t} L${-t - 1},${t} Z`
  if (forma === 'losango') return `M0,${-t - 1} L${t + 1},0 L0,${t + 1} L${-t - 1},0 Z`
  if (forma === 'quadrado') return `M${-t},${-t} H${t} V${t} H${-t} Z`
  return `M${-t},-2 H-2 V${-t} H2 V-2 H${t} V2 H2 V${t} H-2 V2 H${-t} Z`
}

/** A forma ajuda a separar fontes de cor parecida, como Defesa Civil e SEDEC. */
export function Marcador({ x, y, cor, forma, opacidade = 1 }: Propriedades) {
  if (x === undefined || y === undefined) return null
  if (forma === 'anel') {
    return (
      <circle
        cx={x}
        cy={y}
        r={TAMANHO}
        fill={COR.fundo}
        stroke={cor}
        strokeWidth={2}
        opacity={opacidade}
      />
    )
  }
  if (forma === 'circulo') {
    return (
      <circle
        cx={x}
        cy={y}
        r={TAMANHO}
        fill={cor}
        stroke={COR.fundo}
        strokeWidth={2}
        opacity={opacidade}
      />
    )
  }
  return (
    <path
      d={caminhoDaForma(forma)}
      transform={`translate(${x},${y})`}
      fill={cor}
      stroke={COR.fundo}
      strokeWidth={1.5}
      opacity={opacidade}
    />
  )
}
