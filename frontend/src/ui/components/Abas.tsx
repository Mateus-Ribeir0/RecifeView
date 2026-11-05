import { useId, useRef, useState, type KeyboardEvent, type ReactNode } from 'react'

import estilos from './Abas.module.css'

export interface Aba {
  chave: string
  rotulo: string
  conteudo: ReactNode
}

interface Propriedades {
  legenda: string
  abas: readonly Aba[]
}

const PASSO_POR_TECLA: Readonly<Record<string, number>> = { ArrowRight: 1, ArrowLeft: -1 }

export function Abas({ legenda, abas }: Propriedades) {
  const [ativa, definirAtiva] = useState(abas[0]?.chave)
  const prefixo = useId()
  const botoes = useRef(new Map<string, HTMLButtonElement>())
  const atual = abas.find((aba) => aba.chave === ativa) ?? abas[0]

  function moverComTeclado(evento: KeyboardEvent, indice: number) {
    const passo = PASSO_POR_TECLA[evento.key]
    if (!passo) return
    evento.preventDefault()
    const proxima = abas[(indice + passo + abas.length) % abas.length]
    if (!proxima) return
    definirAtiva(proxima.chave)
    botoes.current.get(proxima.chave)?.focus()
  }

  return (
    <>
      <div role="tablist" aria-label={legenda} className={estilos.lista}>
        {abas.map((aba, indice) => (
          <button
            key={aba.chave}
            ref={(elemento) => {
              if (elemento) botoes.current.set(aba.chave, elemento)
            }}
            type="button"
            role="tab"
            id={`${prefixo}-${aba.chave}`}
            aria-selected={aba.chave === atual?.chave}
            tabIndex={aba.chave === atual?.chave ? 0 : -1}
            className={estilos.aba}
            onClick={() => definirAtiva(aba.chave)}
            onKeyDown={(evento) => moverComTeclado(evento, indice)}
          >
            {aba.rotulo}
          </button>
        ))}
      </div>
      <div
        role="tabpanel"
        aria-labelledby={`${prefixo}-${atual?.chave}`}
        className={estilos.painel}
      >
        {atual?.conteudo}
      </div>
    </>
  )
}
