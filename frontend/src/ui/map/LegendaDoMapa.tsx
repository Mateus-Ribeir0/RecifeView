import { formatarNumero } from '../../domain/formatacao'
import estilos from './LegendaDoMapa.module.css'

interface Propriedades {
  titulo: string
  faixas: readonly { inicio: number; fim: number }[]
  casas?: number
}

const CLASSES_DA_ESCALA = 5
const CORES = ['--cor-mapa-1', '--cor-mapa-2', '--cor-mapa-3', '--cor-mapa-4', '--cor-mapa-5']

function corDaFaixa(indice: number, total: number): string {
  const posicao = total >= CLASSES_DA_ESCALA ? indice : indice + CLASSES_DA_ESCALA - total
  return `var(${CORES[posicao] ?? CORES[0]})`
}

export function LegendaDoMapa({ titulo, faixas, casas = 1 }: Propriedades) {
  return (
    <div className={estilos.legenda}>
      <p className={estilos.titulo}>{titulo}</p>
      <ul className={estilos.itens}>
        {faixas.map((faixa, indice) => (
          <li key={faixa.inicio}>
            <span
              className={estilos.marca}
              style={{ background: corDaFaixa(indice, faixas.length) }}
              aria-hidden="true"
            />
            <span className={estilos.limites}>
              <span>
                <span className="visualmente-oculto">de </span>
                {formatarNumero(faixa.inicio, casas)}
              </span>
              {indice === faixas.length - 1 && (
                <span>
                  <span className="visualmente-oculto">a </span>
                  {formatarNumero(faixa.fim, casas)}
                </span>
              )}
            </span>
          </li>
        ))}
        <li className={estilos.semDadoItem}>
          <span className={`${estilos.marca} ${estilos.semDado}`} aria-hidden="true" />
          <span className={estilos.limites}>sem dado</span>
        </li>
      </ul>
    </div>
  )
}
