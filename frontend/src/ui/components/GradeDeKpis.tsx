import type { ReactNode } from 'react'

import estilos from './GradeDeKpis.module.css'

interface Propriedades {
  children: ReactNode
  compacta?: boolean
}

export function GradeDeKpis({ children, compacta }: Propriedades) {
  return <div className={`${estilos.grade} ${compacta ? estilos.compacta : ''}`}>{children}</div>
}
