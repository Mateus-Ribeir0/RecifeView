import { formatarNumero } from '../../domain/formatacao'
import { ESCALA_DO_MAPA } from './estilo'
import estilos from './MapaDeCobertura.module.css'

interface Propriedades {
  fontes: readonly { chave: string; rotulo: string }[]
  celulas: readonly { fonte: string; ano: number; n: number }[]
}

const PRIMEIRA_CLASSE_DE_TEXTO_CLARO = 3

function classeDaCelula(n: number, maximo: number): number {
  const posicao = Math.log10(n + 1) / Math.log10(maximo + 1)
  return Math.min(Math.floor(posicao * ESCALA_DO_MAPA.length), ESCALA_DO_MAPA.length - 1)
}

export function MapaDeCobertura({ fontes, celulas }: Propriedades) {
  const anos = [...new Set(celulas.map((celula) => celula.ano))].sort((a, b) => a - b)
  const maximo = Math.max(...celulas.map((celula) => celula.n), 1)
  const porChave = new Map(celulas.map((celula) => [`${celula.fonte}|${celula.ano}`, celula.n]))

  return (
    <div className={estilos.rolagem}>
      <table className={estilos.tabela}>
        <caption className="visualmente-oculto">Registros por fonte e ano</caption>
        <thead>
          <tr>
            <th scope="col">Fonte</th>
            {anos.map((ano) => (
              <th key={ano} scope="col">
                {ano}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {fontes.map((fonte) => (
            <tr key={fonte.chave}>
              <th scope="row">{fonte.rotulo}</th>
              {anos.map((ano) => {
                const n = porChave.get(`${fonte.chave}|${ano}`)
                if (n === undefined) return <td key={ano} />
                const classe = classeDaCelula(n, maximo)
                const claro = classe >= PRIMEIRA_CLASSE_DE_TEXTO_CLARO
                return (
                  <td
                    key={ano}
                    style={{
                      background: ESCALA_DO_MAPA[classe],
                      color: claro ? 'var(--cor-branco)' : 'var(--cor-preto)',
                    }}
                  >
                    {formatarNumero(n)}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
