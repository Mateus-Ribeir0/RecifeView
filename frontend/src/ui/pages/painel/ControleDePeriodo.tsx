import { useState } from 'react'

import { formatarPeriodo } from '../../../domain/formatacao'
import estilos from './ControleDePeriodo.module.css'

interface Propriedades {
  minimo: number
  maximo: number
  inicio: number
  fim: number
  aoMudar: (inicio: number, fim: number) => void
}

export function ControleDePeriodo({ minimo, maximo, inicio, fim, aoMudar }: Propriedades) {
  const [rascunho, definirRascunho] = useState<{ inicio: number; fim: number } | null>(null)
  const atual = rascunho ?? { inicio, fim }
  const amplitude = Math.max(maximo - minimo, 1)
  const esquerda = ((atual.inicio - minimo) / amplitude) * 100
  const direita = ((maximo - atual.fim) / amplitude) * 100

  function confirmar() {
    if (rascunho) aoMudar(rascunho.inicio, rascunho.fim)
    definirRascunho(null)
  }

  return (
    <div className={estilos.periodo}>
      <div className={estilos.cabecalho}>
        <span className={estilos.rotulo}>Período</span>
        <span className={`${estilos.valor} numero`}>
          {formatarPeriodo(atual.inicio, atual.fim)}
        </span>
      </div>
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
  )
}
