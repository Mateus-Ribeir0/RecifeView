import { COR } from './estilo'
import estilos from './Sparkline.module.css'

interface Propriedades {
  valores: readonly number[]
  rotulo: string
}

const LARGURA = 100
const ALTURA = 32
const FOLGA = 3

export function Sparkline({ valores, rotulo }: Propriedades) {
  if (valores.length < 2) return null
  const minimo = Math.min(...valores)
  const amplitude = Math.max(...valores) - minimo || 1
  const pontos = valores.map((valor, indice) => ({
    x: (indice / (valores.length - 1)) * LARGURA,
    y: ALTURA - FOLGA - ((valor - minimo) / amplitude) * (ALTURA - 2 * FOLGA),
  }))
  const linha = pontos.map(({ x, y }) => `${x},${y}`).join(' ')
  const ultimo = pontos[pontos.length - 1]

  return (
    <div className={estilos.sparkline} role="img" aria-label={rotulo}>
      <svg viewBox={`0 0 ${LARGURA} ${ALTURA}`} preserveAspectRatio="none" aria-hidden="true">
        <polygon
          points={`0,${ALTURA} ${linha} ${LARGURA},${ALTURA}`}
          fill="var(--cor-azul-claro)"
        />
        <polyline
          points={linha}
          fill="none"
          stroke={COR.principal}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      {ultimo && (
        <span
          className={estilos.ponto}
          style={{ top: `${(ultimo.y / ALTURA) * 100}%` }}
          aria-hidden="true"
        />
      )}
    </div>
  )
}
