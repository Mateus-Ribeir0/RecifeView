import type { CSSProperties, ReactNode } from 'react'

import { formatarNumero } from '../../../../domain/formatacao'
import { useVisivelNaTela } from '../../../components/useVisivelNaTela'
import estilos from './Evidencias.module.css'

interface PropriedadesDoQuadro {
  titulo: string
  nota: string
  children: ReactNode
}

function Quadro({ titulo, nota, children }: PropriedadesDoQuadro) {
  const [referencia, visivel] = useVisivelNaTela<HTMLElement>()

  return (
    <figure ref={referencia} className={estilos.quadro} data-visivel={visivel || undefined}>
      <figcaption className={estilos.titulo}>{titulo}</figcaption>
      {children}
      <p className={estilos.nota}>{nota}</p>
    </figure>
  )
}

interface BarraHorizontal {
  rotulo: string
  valor: string
  percentual: number
  emFoco: boolean
}

function BarrasHorizontais({ barras }: { barras: readonly BarraHorizontal[] }) {
  return (
    <ul className={estilos.barras}>
      {barras.map(({ rotulo, valor, percentual, emFoco }, indice) => (
        <li key={rotulo} className={estilos.linha}>
          <span className={estilos.rotulo}>{rotulo}</span>
          <span className={estilos.trilho}>
            <span
              className={estilos.barra}
              data-foco={emFoco || undefined}
              style={
                {
                  '--tamanho': `${percentual}%`,
                  '--atraso': `${indice * 70}ms`,
                } as CSSProperties
              }
            />
          </span>
          <span className={`numero ${estilos.valor}`}>{valor}</span>
        </li>
      ))}
    </ul>
  )
}

const ETAPAS_DO_FUNIL = [
  { rotulo: 'Apresentadas', n: 54810, percentual: 100 },
  { rotulo: 'Enviadas à Prefeitura', n: 53055, percentual: 96.8 },
  { rotulo: 'Com resposta registrada', n: 11243, percentual: 20.5 },
] as const

export function FunilDoRetorno() {
  return (
    <Quadro
      titulo="Quase tudo chega à Prefeitura, mas só uma em cada cinco indicações tem resposta registrada"
      nota="Fonte: SAGL da Câmara Municipal do Recife. Indicações de 2021 a 2025, n = 54.810. Quando existe, a resposta vem em mediana 241 dias depois. Sem resposta registrada não quer dizer que o pedido não foi atendido."
    >
      <BarrasHorizontais
        barras={ETAPAS_DO_FUNIL.map(({ rotulo, n, percentual }, indice) => ({
          rotulo,
          valor: `${formatarNumero(n)} (${formatarNumero(percentual, percentual === 100 ? 0 : 1)}%)`,
          percentual,
          emFoco: indice === ETAPAS_DO_FUNIL.length - 1,
        }))}
      />
    </Quadro>
  )
}

const PARTES_DOS_INTERVALOS = [
  { rotulo: 'Até 7 dias: duplicidade', percentual: 18.5, classe: 'parteClara' },
  { rotulo: '8 a 29 dias', percentual: 17.1, classe: 'parteMedia' },
  { rotulo: '30 dias ou mais: reincidência', percentual: 64.4, classe: 'parteForte' },
] as const

export function IntervalosDaRepeticao() {
  return (
    <Quadro
      titulo="53,3% dos pedidos caem num local e serviço repetidos, e a maior parte volta depois de 30 dias"
      nota="Fonte: Central 156/Emlurb, 2015 a 2025, só pedidos com número no endereço (388.608 de 729.737, definição local e serviço repetidos). Intervalos entre pedidos seguidos no mesmo local e serviço, n = 277.422."
    >
      <div className={estilos.composicao}>
        {PARTES_DOS_INTERVALOS.map(({ rotulo, percentual, classe }) => (
          <span
            key={rotulo}
            className={`${estilos.parte} ${estilos[classe]}`}
            style={{ '--tamanho': `${percentual}%` } as CSSProperties}
          />
        ))}
      </div>
      <ul className={estilos.legenda}>
        {PARTES_DOS_INTERVALOS.map(({ rotulo, percentual, classe }) => (
          <li key={rotulo}>
            <span className={`${estilos.amostra} ${estilos[classe]}`} />
            {rotulo}: <strong className="numero">{formatarNumero(percentual, 1)}%</strong>
          </li>
        ))}
      </ul>
    </Quadro>
  )
}

const PRAZO_P90_POR_ANO = [
  { ano: 2015, dias: 22 },
  { ano: 2016, dias: 37 },
  { ano: 2017, dias: 36 },
  { ano: 2018, dias: 27 },
  { ano: 2019, dias: 20 },
  { ano: 2020, dias: 36 },
  { ano: 2021, dias: 44 },
  { ano: 2022, dias: 48 },
  { ano: 2023, dias: 75 },
  { ano: 2024, dias: 75 },
] as const
const INICIO_DA_ALTA = 2021
const MAIOR_PRAZO = 75

export function PrazoPorAno() {
  return (
    <Quadro
      titulo="Os 10% de pedidos mais demorados passaram de 20 a 37 dias para 44 a 75 dias"
      nota="Fonte: Central 156/Emlurb, pedidos atendidos, 2015 a 2024, n = 739.952. Percentil 90 do tempo até a última movimentação, por ano. Na mesma época, a mediana ficou entre 2 e 5 dias."
    >
      <ol className={estilos.colunas}>
        {PRAZO_P90_POR_ANO.map(({ ano, dias }, indice) => (
          <li key={ano} className={estilos.coluna}>
            <span className={`numero ${estilos.valorDaColuna}`}>{dias}</span>
            <span
              className={estilos.barraVertical}
              data-foco={ano >= INICIO_DA_ALTA || undefined}
              style={
                {
                  '--tamanho': `${(dias / MAIOR_PRAZO) * 100}%`,
                  '--atraso': `${indice * 50}ms`,
                } as CSSProperties
              }
            />
            <span className={`numero ${estilos.ano}`}>{ano}</span>
          </li>
        ))}
      </ol>
    </Quadro>
  )
}

const PARTE_DO_ORGAO_PRINCIPAL = [
  { rotulo: 'Risco', percentual: 38.0, emFoco: true },
  { rotulo: 'Escadarias', percentual: 65.2, emFoco: true },
  { rotulo: 'Praças', percentual: 65.8, emFoco: true },
  { rotulo: 'Pavimentação', percentual: 74.5, emFoco: true },
  { rotulo: 'Iluminação', percentual: 87.5, emFoco: false },
  { rotulo: 'Drenagem', percentual: 88.2, emFoco: false },
  { rotulo: 'Limpeza urbana', percentual: 91.4, emFoco: false },
] as const

export function DestinoDasIndicacoes() {
  return (
    <Quadro
      titulo="Em risco, escadarias, praças e pavimentação, o órgão principal recebe de 38% a 75% das indicações"
      nota="Fonte: SAGL da Câmara Municipal do Recife, 2021 a 2025. Parte do órgão que mais recebe cada categoria. Categoria e órgão são inferidos pelo texto da indicação, por isso são uma aproximação."
    >
      <BarrasHorizontais
        barras={PARTE_DO_ORGAO_PRINCIPAL.map(({ rotulo, percentual, emFoco }) => ({
          rotulo,
          valor: `${formatarNumero(percentual, 1)}%`,
          percentual,
          emFoco,
        }))}
      />
    </Quadro>
  )
}
