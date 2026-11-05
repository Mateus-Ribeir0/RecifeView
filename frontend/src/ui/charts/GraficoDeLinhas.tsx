import { useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO } from './estilo'
import { Legenda } from './Legenda'
import { Marcador, type FormaDoMarcador } from './Marcador'

export interface SerieDeLinha {
  chave: string
  rotulo: string
  cor: string
  forma: FormaDoMarcador
}

type LinhaDeDados = Readonly<Record<string, number | string | null>>

interface Propriedades {
  dados: readonly LinhaDeDados[]
  eixoX: string
  series: readonly SerieDeLinha[]
  rotuloDoEixo: string
  formatar?: (valor: number) => string
  altura?: number
}

interface DicaDeLinha {
  active?: boolean
  label?: string | number
}

export function GraficoDeLinhas({
  dados,
  eixoX,
  series,
  rotuloDoEixo,
  formatar = formatarNumero,
  altura = 360,
}: Propriedades) {
  const [foco, definirFoco] = useState<string | null>(null)

  function desenharDica({ active, label }: DicaDeLinha) {
    if (!active) return null
    const linha = dados.find((item) => item[eixoX] === label)
    if (!linha) return null
    const linhas = series
      .filter((serie) => typeof linha[serie.chave] === 'number')
      .map((serie) => ({
        rotulo: serie.rotulo,
        valor: formatar(linha[serie.chave] as number),
        cor: serie.cor,
      }))
    return <CaixaDeDica titulo={String(label)} linhas={linhas} />
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={altura}>
        <LineChart data={[...dados]} margin={{ top: 8, right: 16, bottom: 0, left: 8 }}>
          <CartesianGrid vertical={false} stroke={COR.grade} />
          <XAxis dataKey={eixoX} {...EIXO} />
          <YAxis
            {...EIXO}
            axisLine={false}
            width={72}
            tickFormatter={(valor: number) => formatarNumero(valor)}
            label={{
              value: rotuloDoEixo,
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12, fill: COR.eixo, textAnchor: 'middle' },
            }}
          />
          <Tooltip content={desenharDica} />
          {series.map((serie) => (
            <Line
              key={serie.chave}
              dataKey={serie.chave}
              name={serie.rotulo}
              stroke={serie.cor}
              strokeWidth={2}
              strokeOpacity={foco && foco !== serie.chave ? 0.15 : 1}
              connectNulls={false}
              dot={(ponto) => (
                <Marcador
                  key={`${serie.chave}-${ponto.index}`}
                  x={ponto.cx}
                  y={ponto.cy}
                  cor={serie.cor}
                  forma={serie.forma}
                  opacidade={foco && foco !== serie.chave ? 0.15 : 1}
                />
              )}
              {...ANIMACAO}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <Legenda
        itens={series.map(({ chave, rotulo, cor }) => ({ chave, rotulo, cor }))}
        foco={foco}
        aoEscolher={definirFoco}
      />
    </div>
  )
}
