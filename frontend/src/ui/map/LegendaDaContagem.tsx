import type { FaixaDaContagem } from '../../domain/classes'
import { formatarNumero } from '../../domain/formatacao'
import estilos from './LegendaDoMapa.module.css'

const CORES = ['--cor-mapa-1', '--cor-mapa-2', '--cor-mapa-3', '--cor-mapa-4', '--cor-mapa-5']

function limites({ inicio, fim }: FaixaDaContagem): string {
  return inicio === fim
    ? formatarNumero(inicio)
    : `${formatarNumero(inicio)} a ${formatarNumero(fim)}`
}

interface Propriedades {
  titulo: string
  faixas: readonly FaixaDaContagem[]
}

/** Cada cor com a contagem escrita: zero sempre na mais clara, como no mapa. */
export function LegendaDaContagem({ titulo, faixas }: Propriedades) {
  return (
    <div className={estilos.legenda}>
      <p className={estilos.titulo}>{titulo}</p>
      <ul className={estilos.itens}>
        {faixas.map((faixa) => (
          <li key={faixa.classe}>
            <span
              className={estilos.marca}
              style={{ background: `var(${CORES[faixa.classe - 1] ?? CORES[0]})` }}
              aria-hidden="true"
            />
            <span className={estilos.limites}>{limites(faixa)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
