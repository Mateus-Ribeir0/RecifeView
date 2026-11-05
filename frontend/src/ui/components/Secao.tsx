import type { ReactNode } from 'react'

import { Dica } from './Dica'
import estilos from './Secao.module.css'

interface Propriedades {
  titulo: string
  ajuda?: string
  children: ReactNode
}

export function Secao({ titulo, ajuda, children }: Propriedades) {
  return (
    <section className={estilos.secao}>
      <h2 className={estilos.titulo}>
        {titulo}
        {ajuda && <Dica texto={ajuda} />}
      </h2>
      {children}
    </section>
  )
}

export function Colunas({ children, proporcao }: { children: ReactNode; proporcao?: 'larga' }) {
  const classe = proporcao === 'larga' ? estilos.colunasLarga : estilos.colunas
  return <div className={classe}>{children}</div>
}
