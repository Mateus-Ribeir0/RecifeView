import { Fragment } from 'react'

import { formatarNumero } from '../../domain/formatacao'
import estilos from './MapaDeCalor.module.css'
import { ESCALA_DO_MAPA } from './estilo'

export interface CelulaDoMapaDeCalor {
  linha: string
  coluna: string
  pct: number
  n: number
}

interface Propriedades {
  linhas: readonly { chave: string; rotulo: string }[]
  colunas: readonly { chave: string; rotulo: string }[]
  celulas: readonly CelulaDoMapaDeCalor[]
  selecionada: string | null
  aoSelecionar: (linha: string) => void
}

const PCT_DE_TEXTO_CLARO = 55
const PONTOS_POR_CLASSE = 20

function corDaCelula(pct: number): string {
  const classe = Math.min(Math.floor(pct / PONTOS_POR_CLASSE), ESCALA_DO_MAPA.length - 1)
  return ESCALA_DO_MAPA[classe] ?? 'transparent'
}

export function MapaDeCalor({ linhas, colunas, celulas, selecionada, aoSelecionar }: Propriedades) {
  const porChave = new Map(celulas.map((celula) => [`${celula.linha}|${celula.coluna}`, celula]))
  const grade = `minmax(100px, 150px) repeat(${colunas.length}, minmax(46px, 1fr))`

  return (
    <div className={estilos.rolagem}>
      <div className={estilos.mapa} style={{ gridTemplateColumns: grade }} role="table">
        <span role="columnheader" />
        {colunas.map((coluna) => (
          <span key={coluna.chave} role="columnheader" className={estilos.cabecalho}>
            {coluna.rotulo}
          </span>
        ))}
        {linhas.map((linha) => {
          const apagada = selecionada !== null && selecionada !== linha.chave
          return (
            <Fragment key={linha.chave}>
              <button
                type="button"
                role="rowheader"
                className={estilos.rotulo}
                aria-pressed={selecionada === linha.chave}
                onClick={() => aoSelecionar(linha.chave)}
              >
                {linha.rotulo}
              </button>
              {colunas.map((coluna) => {
                const celula = porChave.get(`${linha.chave}|${coluna.chave}`)
                const pct = celula?.pct ?? 0
                return (
                  <button
                    key={coluna.chave}
                    type="button"
                    role="cell"
                    className={estilos.celula}
                    style={{
                      background: celula ? corDaCelula(pct) : undefined,
                      color: pct > PCT_DE_TEXTO_CLARO ? 'var(--cor-branco)' : 'var(--cor-preto)',
                      opacity: apagada ? 0.35 : 1,
                    }}
                    title={`${linha.rotulo}, ${coluna.rotulo}: ${formatarNumero(pct)}% (${formatarNumero(celula?.n ?? 0)} indicações)`}
                    onClick={() => aoSelecionar(linha.chave)}
                  >
                    {celula ? formatarNumero(pct) : ''}
                  </button>
                )
              })}
            </Fragment>
          )
        })}
      </div>
    </div>
  )
}
