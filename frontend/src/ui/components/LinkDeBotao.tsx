import type { ReactNode } from 'react'
import { Link } from 'react-router'

import { classesDoBotao, type VarianteDoBotao } from './classesDoBotao'

interface Propriedades {
  para: string
  variante?: VarianteDoBotao
  compacto?: boolean
  children: ReactNode
}

export function LinkDeBotao({ para, variante = 'primario', compacto, children }: Propriedades) {
  const classes = classesDoBotao(variante, { compacto })
  if (para.startsWith('#')) {
    return (
      <a href={para} className={classes}>
        {children}
      </a>
    )
  }
  return (
    <Link to={para} className={classes}>
      {children}
    </Link>
  )
}
