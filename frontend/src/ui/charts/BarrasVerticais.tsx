import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO, RAIO_DA_BARRA_VERTICAL } from './estilo'

export interface ColunaDoGrafico {
  rotulo: string
  valor: number
  texto: string
  detalhe?: string
  cor?: string
}

interface Propriedades {
  dados: readonly ColunaDoGrafico[]
  rotuloDoEixo: string
  maximo?: number
  altura?: number
  larguraDaBarra?: number
}

interface DicaDeColuna {
  active?: boolean
  label?: string | number
}

interface RotuloDoEixo {
  x?: number | string
  y?: number | string
  payload?: { value?: string | number }
}

function desenharRotulo({ x, y, payload }: RotuloDoEixo) {
  const linhas = String(payload?.value ?? '').split('\n')
  return (
    <text x={x} y={y} textAnchor="middle" fontSize={12} fontWeight={500} fill={COR.eixo}>
      {linhas.map((linha, indice) => (
        <tspan key={linha} x={x} dy={indice === 0 ? 12 : 14}>
          {linha}
        </tspan>
      ))}
    </text>
  )
}

export function BarrasVerticais({
  dados,
  rotuloDoEixo,
  maximo,
  altura = 300,
  larguraDaBarra = 40,
}: Propriedades) {
  function desenharDica({ active, label }: DicaDeColuna) {
    const coluna = dados.find((item) => item.rotulo === label)
    if (!active || !coluna) return null
    const linhas = [{ rotulo: coluna.detalhe ?? rotuloDoEixo, valor: coluna.texto }]
    return <CaixaDeDica titulo={coluna.rotulo.replace('\n', ', ')} linhas={linhas} />
  }

  return (
    <ResponsiveContainer width="100%" height={altura}>
      <BarChart data={[...dados]} margin={{ top: 24, right: 8, bottom: 0, left: 8 }}>
        <CartesianGrid vertical={false} stroke={COR.grade} />
        <XAxis dataKey="rotulo" {...EIXO} interval={0} height={44} tick={desenharRotulo} />
        <YAxis
          {...EIXO}
          axisLine={false}
          width={56}
          domain={[0, maximo ?? 'auto']}
          tickFormatter={(valor: number) => formatarNumero(valor)}
        />
        <Tooltip content={desenharDica} cursor={{ fill: 'var(--cor-azul-claro)' }} />
        <Bar
          dataKey="valor"
          barSize={larguraDaBarra}
          radius={RAIO_DA_BARRA_VERTICAL}
          fill={COR.principal}
          {...ANIMACAO}
        >
          {dados.map((item) => (
            <Cell key={item.rotulo} fill={item.cor ?? COR.principal} />
          ))}
          <LabelList dataKey="texto" position="top" fontSize={12} fill={COR.texto} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
