import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO, LARGURA_MAXIMA_DA_BARRA } from './estilo'
import { Legenda } from './Legenda'

export interface SegmentoDoEmpilhado {
  chave: string
  rotulo: string
  cor: string
}

type LinhaEmpilhada = Readonly<Record<string, number | string>>

interface Propriedades {
  dados: readonly LinhaEmpilhada[]
  eixo: string
  segmentos: readonly SegmentoDoEmpilhado[]
  orientacao: 'vertical' | 'horizontal'
  emPercentual?: boolean
  maximo?: number
  formatar?: (valor: number) => string
  larguraDoRotulo?: number
  altura?: number
}

interface DicaEmpilhada {
  active?: boolean
  label?: string | number
}

const ALTURA_DA_LINHA = 28
const MARCAS_DO_EIXO = 5

export function BarrasEmpilhadas({
  dados,
  eixo,
  segmentos,
  orientacao,
  emPercentual,
  maximo,
  formatar = formatarNumero,
  larguraDoRotulo = 200,
  altura = 300,
}: Propriedades) {
  const horizontal = orientacao === 'horizontal'
  const alturaFinal = horizontal ? dados.length * ALTURA_DA_LINHA + 40 : altura

  function desenharDica({ active, label }: DicaEmpilhada) {
    const linha = dados.find((item) => item[eixo] === label)
    if (!active || !linha) return null
    const linhas = segmentos.map((segmento) => ({
      rotulo: segmento.rotulo,
      valor: formatar(Number(linha[segmento.chave] ?? 0)),
      cor: segmento.cor,
    }))
    return <CaixaDeDica titulo={String(label)} linhas={linhas} />
  }

  const eixoDeValor = {
    type: 'number' as const,
    ...EIXO,
    domain: [0, emPercentual ? 1 : (maximo ?? 'auto')] as [number, number | 'auto'],
    ticks: maximo
      ? Array.from(
          { length: MARCAS_DO_EIXO + 1 },
          (_, indice) => (maximo / MARCAS_DO_EIXO) * indice,
        )
      : undefined,
    tickFormatter: (valor: number) =>
      emPercentual ? `${formatarNumero(valor * 100)}%` : formatarNumero(valor),
  }
  const eixoDeCategoria = { type: 'category' as const, dataKey: eixo, ...EIXO, interval: 0 }

  return (
    <div>
      <ResponsiveContainer width="100%" height={alturaFinal}>
        <BarChart
          data={[...dados]}
          layout={horizontal ? 'vertical' : 'horizontal'}
          stackOffset={emPercentual ? 'expand' : 'none'}
          margin={{ top: 8, right: 16, bottom: 0, left: 8 }}
        >
          <CartesianGrid horizontal={!horizontal} vertical={horizontal} stroke={COR.grade} />
          {horizontal ? (
            <>
              <XAxis {...eixoDeValor} />
              <YAxis
                {...eixoDeCategoria}
                width={larguraDoRotulo}
                tick={{ fontSize: 12, fill: COR.texto }}
              />
            </>
          ) : (
            <>
              <XAxis {...eixoDeCategoria} />
              <YAxis {...eixoDeValor} axisLine={false} width={56} />
            </>
          )}
          <Tooltip content={desenharDica} cursor={{ fill: 'var(--cor-azul-claro)' }} />
          {segmentos.map((segmento) => (
            <Bar
              key={segmento.chave}
              dataKey={segmento.chave}
              name={segmento.rotulo}
              stackId="total"
              fill={segmento.cor}
              stroke={COR.fundo}
              strokeWidth={1}
              barSize={horizontal ? 18 : LARGURA_MAXIMA_DA_BARRA + 12}
              {...ANIMACAO}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
      <Legenda itens={segmentos} />
    </div>
  )
}
