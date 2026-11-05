import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { Ponto } from '../../domain/painel'
import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO } from './estilo'

export interface PontoDeBairro extends Ponto {
  nome: string
  emDestaque: boolean
}

interface Propriedades {
  pontos: readonly PontoDeBairro[]
  tendencia: readonly Ponto[]
  rotuloX: string
  rotuloY: string
  escalaLog?: boolean
}

interface DicaDeDispersao {
  active?: boolean
  payload?: readonly { payload?: Partial<PontoDeBairro> & { yGrafico?: number } }[]
}

const MARCAS_DA_ESCALA_LOG = [0, 1, 3, 10, 30, 100]

function emEscalaLog(valor: number): number {
  return Math.log10(1 + Math.max(valor, 0))
}

function daEscalaLog(valor: number): number {
  return 10 ** valor - 1
}

export function GraficoDeDispersao({
  pontos,
  tendencia,
  rotuloX,
  rotuloY,
  escalaLog,
}: Propriedades) {
  const transformar = escalaLog ? emEscalaLog : (valor: number) => valor
  const dados = pontos.map((ponto) => ({ ...ponto, yGrafico: transformar(ponto.y) }))
  const linha = tendencia.map((ponto) => ({ x: ponto.x, yGrafico: transformar(ponto.y) }))

  function desenharDica({ active, payload }: DicaDeDispersao) {
    const ponto = payload?.[0]?.payload
    if (!active || !ponto?.nome) return null
    const valorY = escalaLog ? daEscalaLog(ponto.yGrafico ?? 0) : (ponto.y ?? 0)
    return (
      <CaixaDeDica
        titulo={ponto.nome}
        linhas={[
          { rotulo: rotuloX, valor: `${formatarNumero(ponto.x ?? 0, 1)}%` },
          { rotulo: rotuloY, valor: formatarNumero(valorY, 1) },
        ]}
      />
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 24, left: 8 }}>
        <CartesianGrid vertical={false} stroke={COR.grade} />
        <XAxis
          type="number"
          dataKey="x"
          {...EIXO}
          domain={[0, 'auto']}
          label={{
            value: rotuloX,
            position: 'insideBottom',
            offset: -12,
            style: { fontSize: 12, fill: COR.eixo },
          }}
        />
        <YAxis
          type="number"
          dataKey="yGrafico"
          {...EIXO}
          axisLine={false}
          width={56}
          ticks={escalaLog ? MARCAS_DA_ESCALA_LOG.map(emEscalaLog) : undefined}
          tickFormatter={(valor: number) =>
            formatarNumero(escalaLog ? Math.round(daEscalaLog(valor)) : valor)
          }
          label={{
            value: rotuloY,
            angle: -90,
            position: 'insideLeft',
            style: { fontSize: 12, fill: COR.eixo, textAnchor: 'middle' },
          }}
        />
        <Tooltip content={desenharDica} cursor={false} />
        <Scatter
          data={dados}
          shape={(propriedades: { cx?: number; cy?: number; payload?: PontoDeBairro }) => (
            <circle
              cx={propriedades.cx}
              cy={propriedades.cy}
              r={5}
              fill={propriedades.payload?.emDestaque ? COR.principal : COR.claro}
              stroke={COR.fundo}
              strokeWidth={1}
            />
          )}
          {...ANIMACAO}
        />
        <Scatter
          data={linha}
          line={{ stroke: COR.marinho, strokeWidth: 2 }}
          shape={() => <g />}
          legendType="none"
          tooltipType="none"
          {...ANIMACAO}
        />
      </ScatterChart>
    </ResponsiveContainer>
  )
}
