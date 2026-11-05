import type { ReactNode } from 'react'

import estilos from './GradeDeKpis.module.css'

export function GradeDeKpis({ children }: { children: ReactNode }) {
  return <div className={estilos.grade}>{children}</div>
}
