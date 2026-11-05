import type { ReactNode } from 'react'

import estilos from './Tabela.module.css'

export interface ColunaDaTabela<T> {
  titulo: string
  ajuda?: string
  numerica?: boolean
  valor: (linha: T) => ReactNode
}

interface Propriedades<T> {
  legenda: string
  colunas: readonly ColunaDaTabela<T>[]
  linhas: readonly T[]
  chave: (linha: T, indice: number) => string
  altura?: number
}

export function Tabela<T>({ legenda, colunas, linhas, chave, altura }: Propriedades<T>) {
  return (
    <div className={estilos.rolagem} style={altura ? { maxHeight: altura } : undefined}>
      <table className={estilos.tabela}>
        <caption className="visualmente-oculto">{legenda}</caption>
        <thead>
          <tr>
            {colunas.map((coluna) => (
              <th
                key={coluna.titulo}
                scope="col"
                title={coluna.ajuda}
                className={coluna.numerica ? estilos.numerica : undefined}
              >
                {coluna.titulo}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {linhas.map((linha, indice) => (
            <tr key={chave(linha, indice)}>
              {colunas.map((coluna) => (
                <td key={coluna.titulo} className={coluna.numerica ? estilos.numerica : undefined}>
                  {coluna.valor(linha)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
