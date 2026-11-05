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

const CLASSE_DA_PROPORCAO = {
  igual: estilos.colunas,
  larga: estilos.colunasLarga,
  tres: estilos.colunasTres,
}

interface PropriedadesDasColunas {
  children: ReactNode
  proporcao?: keyof typeof CLASSE_DA_PROPORCAO
}

export function Colunas({ children, proporcao = 'igual' }: PropriedadesDasColunas) {
  return <div className={CLASSE_DA_PROPORCAO[proporcao]}>{children}</div>
}
