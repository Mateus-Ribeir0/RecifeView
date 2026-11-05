import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { CaixaDeDica } from './CaixaDeDica'
import { ANIMACAO, COR, EIXO, LARGURA_MAXIMA_DA_BARRA, RAIO_DA_BARRA_HORIZONTAL } from './estilo'

export interface BarraDoGrafico {
  chave: string
  rotulo: string
  valor: number
  texto: string
  detalhe?: string
  cor?: string
}

interface Propriedades {
  dados: readonly BarraDoGrafico[]
  maximo: number
  selecionada?: string | null
  aoSelecionar?: (chave: string | null) => void
  larguraDoRotulo?: number
  rotuloDoValor?: string
  alturaDaLinha?: number
}

interface DicaDeBarra {
  active?: boolean
  label?: string | number
}

const MARGEM_DO_TEXTO = 1.28

export function BarrasHorizontais({
  dados,
  maximo,
  selecionada,
  aoSelecionar,
  larguraDoRotulo = 200,
  rotuloDoValor = 'valor',
  alturaDaLinha = 32,
}: Propriedades) {
  function desenharDica({ active, label }: DicaDeBarra) {
    const barra = dados.find((item) => item.rotulo === label)
    if (!active || !barra) return null
    const linhas = [{ rotulo: barra.detalhe ?? rotuloDoValor, valor: barra.texto }]
    return <CaixaDeDica titulo={barra.rotulo} linhas={linhas} />
  }

  const haSelecao = dados.some((item) => item.chave === selecionada)

  function corDaBarra(item: BarraDoGrafico): string {
    if (item.cor) return item.cor
    if (!haSelecao) return COR.principal
    return selecionada === item.chave ? COR.principal : COR.claro
  }

  return (
    <ResponsiveContainer width="100%" height={dados.length * alturaDaLinha + 16}>
      <BarChart
        data={[...dados]}
        layout="vertical"
        margin={{ top: 8, right: 16, bottom: 0, left: 0 }}
      >
        <XAxis type="number" hide domain={[0, maximo * MARGEM_DO_TEXTO]} />
        <YAxis
          type="category"
          dataKey="rotulo"
          width={larguraDoRotulo}
          {...EIXO}
          tick={{ fontSize: 12, fill: COR.texto }}
          interval={0}
        />
        <Tooltip content={desenharDica} cursor={{ fill: 'var(--cor-azul-claro)' }} />
        <Bar
          dataKey="valor"
          barSize={Math.min(LARGURA_MAXIMA_DA_BARRA, alturaDaLinha - 8)}
          radius={RAIO_DA_BARRA_HORIZONTAL}
          cursor={aoSelecionar ? 'pointer' : undefined}
          onClick={(_, indice) => {
            const chave = dados[indice]?.chave
            if (!aoSelecionar || !chave) return
            aoSelecionar(selecionada === chave ? null : chave)
          }}
          {...ANIMACAO}
        >
          {dados.map((item) => (
            <Cell key={item.chave} fill={corDaBarra(item)} />
          ))}
          <LabelList dataKey="texto" position="right" fontSize={12} fill={COR.texto} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
