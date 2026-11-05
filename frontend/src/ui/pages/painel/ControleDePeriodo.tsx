import { useState } from 'react'

import { FILTROS_PADRAO } from '../../../domain/filtros'
import { formatarPeriodo } from '../../../domain/formatacao'
import estilos from './ControleDePeriodo.module.css'
import { FiltroSuspenso } from './FiltroSuspenso'

interface Propriedades {
  minimo: number
  maximo: number
  inicio: number
  fim: number
  aoMudar: (inicio: number, fim: number) => void
}

function atalhosDoPeriodo(minimo: number, maximo: number) {
  const { anoInicio, anoFim } = FILTROS_PADRAO
  return [
    { rotulo: 'Período padrão', inicio: anoInicio, fim: anoFim },
    { rotulo: 'Último ano completo', inicio: anoFim, fim: anoFim },
    { rotulo: 'Toda a série', inicio: minimo, fim: maximo },
  ]
}

export function ControleDePeriodo({ minimo, maximo, inicio, fim, aoMudar }: Propriedades) {
  const [rascunho, definirRascunho] = useState<{ inicio: number; fim: number } | null>(null)
  const atual = rascunho ?? { inicio, fim }
  const amplitude = Math.max(maximo - minimo, 1)
  const esquerda = ((atual.inicio - minimo) / amplitude) * 100
  const direita = ((maximo - atual.fim) / amplitude) * 100
  const padrao = inicio === FILTROS_PADRAO.anoInicio && fim === FILTROS_PADRAO.anoFim

  function confirmar() {
    if (rascunho) aoMudar(rascunho.inicio, rascunho.fim)
    definirRascunho(null)
  }

  return (
    <FiltroSuspenso
      rotulo="Período"
      valor={formatarPeriodo(atual.inicio, atual.fim)}
      ativo={!padrao}
    >
      <div className={estilos.periodo}>
        <ul className={estilos.atalhos}>
          {atalhosDoPeriodo(minimo, maximo).map((atalho) => (
            <li key={atalho.rotulo}>
              <button
                type="button"
                className={estilos.atalho}
                aria-pressed={atalho.inicio === inicio && atalho.fim === fim}
                onClick={() => aoMudar(atalho.inicio, atalho.fim)}
              >
                <span>{atalho.rotulo}</span>
                <span className="numero">{formatarPeriodo(atalho.inicio, atalho.fim)}</span>
              </button>
            </li>
          ))}
        </ul>
        <div className={estilos.trilho}>
          <span
            className={estilos.faixa}
            style={{ left: `${esquerda}%`, right: `${direita}%` }}
            aria-hidden="true"
          />
          <input
            type="range"
            aria-label="Ano inicial"
            min={minimo}
            max={maximo}
            value={atual.inicio}
            onChange={(evento) => {
              const valor = Math.min(Number(evento.target.value), atual.fim)
              definirRascunho({ inicio: valor, fim: atual.fim })
            }}
            onPointerUp={confirmar}
            onKeyUp={confirmar}
          />
          <input
            type="range"
            aria-label="Ano final"
            min={minimo}
            max={maximo}
            value={atual.fim}
            onChange={(evento) => {
              const valor = Math.max(Number(evento.target.value), atual.inicio)
              definirRascunho({ inicio: atual.inicio, fim: valor })
            }}
            onPointerUp={confirmar}
            onKeyUp={confirmar}
          />
        </div>
        <div className={`${estilos.extremos} numero`} aria-hidden="true">
          <span>{minimo}</span>
          <span>{maximo}</span>
        </div>
      </div>
    </FiltroSuspenso>
  )
}
