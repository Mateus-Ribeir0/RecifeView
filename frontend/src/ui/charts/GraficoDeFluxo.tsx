import {
  Layer,
  Rectangle,
  ResponsiveContainer,
  Sankey,
  Tooltip,
  type TooltipContentProps,
} from 'recharts'

import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { COR } from './estilo'

export interface NoDoFluxo {
  name: string
  cor: string
}

export interface LigacaoDoFluxo {
  source: number
  target: number
  value: number
}

interface Propriedades {
  nos: readonly NoDoFluxo[]
  ligacoes: readonly LigacaoDoFluxo[]
  altura?: number
}

interface PropriedadesDoNo {
  x: number
  y: number
  width: number
  height: number
  index: number
  payload: { name: string; value: number }
}

const LARGURA_DO_NO = 12
const DISTANCIA_DO_ROTULO = 6
const MARGEM_DOS_ROTULOS = 124

export function GraficoDeFluxo({ nos, ligacoes, altura = 400 }: Propriedades) {
  const nosComSaida = new Set(ligacoes.map((ligacao) => ligacao.source))

  function desenharNo({ x, y, width, height, index, payload }: PropriedadesDoNo) {
    const noFim = !nosComSaida.has(index)
    return (
      <Layer key={`no-${index}`}>
        <Rectangle x={x} y={y} width={width} height={height} fill={nos[index]?.cor ?? COR.medio} />
        {index > 0 && (
          <text
            x={noFim ? x + width + DISTANCIA_DO_ROTULO : x - DISTANCIA_DO_ROTULO}
            y={y + height / 2}
            textAnchor={noFim ? 'start' : 'end'}
            dominantBaseline="middle"
            fontSize={12}
            fill={COR.texto}
          >
            {payload.name} ({formatarNumero(payload.value)})
          </text>
        )}
      </Layer>
    )
  }

  function desenharDica({ active, payload }: TooltipContentProps) {
    const item = payload[0]
    if (!active || !item) return null
    const valor = formatarNumero(Number(item.value ?? 0))
    return <CaixaDeDica linhas={[{ rotulo: String(item.name ?? ''), valor }]} />
  }

  return (
    <ResponsiveContainer width="100%" height={altura}>
      <Sankey
        data={{ nodes: nos.map(({ name }) => ({ name })), links: [...ligacoes] }}
        node={desenharNo}
        nodeWidth={LARGURA_DO_NO}
        nodePadding={20}
        margin={{ top: 8, right: MARGEM_DOS_ROTULOS, bottom: 8, left: 8 }}
        link={{ stroke: COR.claro, strokeOpacity: 0.5 }}
      >
        <Tooltip content={desenharDica} />
      </Sankey>
    </ResponsiveContainer>
  )
}
