import { useEffect, useRef, useState, type ReactNode } from 'react'

import { Icone } from '../../components/Icone'
import estilos from './FiltroSuspenso.module.css'

interface Propriedades {
  rotulo: string
  valor: string
  ativo: boolean
  children: ReactNode
}

export function FiltroSuspenso({ rotulo, valor, ativo, children }: Propriedades) {
  const [aberto, definirAberto] = useState(false)
  const raiz = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!aberto) return
    function fecharAoClicarFora(evento: PointerEvent) {
      if (!raiz.current?.contains(evento.target as Node)) definirAberto(false)
    }
    function fecharComEsc(evento: KeyboardEvent) {
      if (evento.key === 'Escape') definirAberto(false)
    }
    document.addEventListener('pointerdown', fecharAoClicarFora)
    document.addEventListener('keydown', fecharComEsc)
    return () => {
      document.removeEventListener('pointerdown', fecharAoClicarFora)
      document.removeEventListener('keydown', fecharComEsc)
    }
  }, [aberto])

  return (
    <div className={estilos.filtro} ref={raiz}>
      <button
        type="button"
        className={`${estilos.gatilho} ${ativo ? estilos.ativo : ''}`}
        aria-expanded={aberto}
        onClick={() => definirAberto((atual) => !atual)}
      >
        <span className={estilos.rotulo}>{rotulo}</span>
        <span className={estilos.valor}>{valor}</span>
        <Icone nome="abrir" tamanho={16} />
      </button>
      {aberto && (
        <div className={estilos.painel} role="group" aria-label={rotulo}>
          {children}
        </div>
      )}
    </div>
  )
}
