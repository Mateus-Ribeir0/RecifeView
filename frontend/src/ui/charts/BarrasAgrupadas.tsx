import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO } from './estilo'
import { Legenda } from './Legenda'

export interface SerieAgrupada {
  chave: string
  rotulo: string
  cor: string
}

type LinhaAgrupada = Readonly<Record<string, number | string>>

interface Propriedades {
  dados: readonly LinhaAgrupada[]
  eixo: string
  series: readonly SerieAgrupada[]
  altura?: number
}

interface DicaAgrupada {
  active?: boolean
  label?: string | number
}

export function BarrasAgrupadas({ dados, eixo, series, altura = 260 }: Propriedades) {
  function desenharDica({ active, label }: DicaAgrupada) {
    const linha = dados.find((item) => item[eixo] === label)
    if (!active || !linha) return null
    const linhas = series.map((serie) => ({
      rotulo: serie.rotulo,
      valor: formatarNumero(Number(linha[serie.chave] ?? 0)),
      cor: serie.cor,
    }))
    return <CaixaDeDica titulo={String(label)} linhas={linhas} />
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={altura}>
        <BarChart data={[...dados]} margin={{ top: 8, right: 8, bottom: 0, left: 0 }} barGap={0}>
          <CartesianGrid vertical={false} stroke={COR.grade} />
          <XAxis dataKey={eixo} {...EIXO} minTickGap={16} />
          <YAxis
            {...EIXO}
            axisLine={false}
            width={48}
            tickFormatter={(valor: number) => formatarNumero(valor)}
          />
          <Tooltip content={desenharDica} cursor={{ fill: 'var(--cor-azul-claro)' }} />
          {series.map((serie) => (
            <Bar key={serie.chave} dataKey={serie.chave} fill={serie.cor} {...ANIMACAO} />
          ))}
        </BarChart>
      </ResponsiveContainer>
      <Legenda itens={series} />
    </div>
  )
}
