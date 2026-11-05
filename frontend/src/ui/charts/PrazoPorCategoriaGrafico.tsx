import { formatarDias, formatarNumero, formatarPorcentagem } from '../../domain/formatacao'
import estilos from './PrazoPorCategoriaGrafico.module.css'

export interface PrazoDoGrafico {
  nome: string
  mediana: number
  p90: number
  pedidos: number
  pctMesmoDia: number
}

interface Propriedades {
  dados: readonly PrazoDoGrafico[]
}

const MARCAS = [0, 7, 30, 90, 365, 1095, 3650]
const DIAS_MAXIMOS = 4000
const POSICAO_MAXIMA = Math.log10(DIAS_MAXIMOS + 1)

function posicao(dias: number): string {
  return `${(Math.log10(dias + 1) / POSICAO_MAXIMA) * 100}%`
}

export function PrazoPorCategoriaGrafico({ dados }: Propriedades) {
  return (
    <div>
      <ul className={estilos.lista}>
        {dados.map((item) => {
          const dica =
            `${item.nome}: mediana ${formatarDias(item.mediana)}, p90 ${formatarDias(item.p90)}, ` +
            `${formatarPorcentagem(item.pctMesmoDia)} no mesmo dia, ` +
            `${formatarNumero(item.pedidos)} pedidos`
          return (
            <li key={item.nome} className={estilos.linha} title={dica}>
              <span className={estilos.nome}>{item.nome}</span>
              <span className={estilos.trilho}>
                {MARCAS.map((dias) => (
                  <span key={dias} className={estilos.grade} style={{ left: posicao(dias) }} />
                ))}
                <span
                  className={estilos.faixa}
                  style={{
                    left: posicao(item.mediana),
                    width: `calc(${posicao(item.p90)} - ${posicao(item.mediana)})`,
                  }}
                />
                <span className={estilos.mediana} style={{ left: posicao(item.mediana) }} />
                <span className={estilos.p90} style={{ left: posicao(item.p90) }} />
              </span>
            </li>
          )
        })}
      </ul>
      <div className={estilos.eixo}>
        <span />
        <span className={estilos.marcas}>
          {MARCAS.map((dias) => (
            <span key={dias} style={{ left: posicao(dias) }}>
              {formatarNumero(dias)}
            </span>
          ))}
        </span>
      </div>
      <p className={estilos.legenda}>
        <span className={estilos.chaveMediana} aria-hidden="true" /> mediana
        <span className={estilos.chaveP90} aria-hidden="true" /> p90 · dias até atender (escala log)
      </p>
    </div>
  )
}
