import type { CSSProperties, ReactNode } from 'react'

import estilos from './Aparecer.module.css'
import { useVisivelNaTela } from './useVisivelNaTela'

interface Propriedades {
  children: ReactNode
  atraso?: number
  className?: string
}

export function Aparecer({ children, atraso = 0, className }: Propriedades) {
  const [referencia, visivel] = useVisivelNaTela<HTMLDivElement>()
  const estilo = { '--atraso': `${atraso}ms` } as CSSProperties

  return (
    <div
      ref={referencia}
      style={estilo}
      data-visivel={visivel || undefined}
      className={[estilos.aparecer, className].filter(Boolean).join(' ')}
    >
      {children}
    </div>
  )
}
