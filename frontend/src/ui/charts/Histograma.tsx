import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { formatarNumero } from '../../domain/formatacao'
import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO } from './estilo'

export interface FaixaDoHistograma {
  inicio: number
  fim: number
  registros: number
}

export interface MarcaDoHistograma {
  rotulo: string
  valor: number
}

interface Propriedades {
  faixas: readonly FaixaDoHistograma[]
  marcas: readonly MarcaDoHistograma[]
  rotuloDoEixo: string
}

interface DicaDoHistograma {
  active?: boolean
  label?: string | number
}

const DEGRAU_DAS_MARCAS = 14

function rotuloDaFaixa(faixa: FaixaDoHistograma): string {
  return `${formatarNumero(faixa.inicio, 1)} a ${formatarNumero(faixa.fim, 1)}`
}

export function Histograma({ faixas, marcas, rotuloDoEixo }: Propriedades) {
  const dados = faixas.map((faixa) => ({ ...faixa, rotulo: rotuloDaFaixa(faixa) }))

  function desenharDica({ active, label }: DicaDoHistograma) {
    const faixa = dados.find((item) => item.rotulo === label)
    if (!active || !faixa) return null
    const linhas = [{ rotulo: rotuloDoEixo, valor: formatarNumero(faixa.registros) }]
    return <CaixaDeDica titulo={`Nota ${faixa.rotulo}`} linhas={linhas} />
  }

  function faixaDaNota(nota: number): string | undefined {
    return dados.find((item) => nota > item.inicio && nota <= item.fim)?.rotulo ?? dados[0]?.rotulo
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={dados} margin={{ top: 48, right: 8, bottom: 0, left: 8 }} barCategoryGap={1}>
        <CartesianGrid vertical={false} stroke={COR.grade} />
        <XAxis
          dataKey="rotulo"
          {...EIXO}
          interval={3}
          tickFormatter={(rotulo: string) => rotulo.split(' a ')[0] ?? rotulo}
        />
        <YAxis
          {...EIXO}
          axisLine={false}
          width={56}
          tickFormatter={(valor: number) => formatarNumero(valor)}
        />
        <Tooltip content={desenharDica} cursor={{ fill: 'var(--cor-azul-claro)' }} />
        <Bar dataKey="registros" fill={COR.claro} {...ANIMACAO} />
        {marcas.map((marca, indice) => (
          <ReferenceLine
            key={marca.rotulo}
            x={faixaDaNota(marca.valor)}
            stroke={COR.texto}
            strokeWidth={2}
            label={{
              value: marca.rotulo,
              position: 'top',
              offset: 4 + indice * DEGRAU_DAS_MARCAS,
              fontSize: 12,
              fill: COR.texto,
            }}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
