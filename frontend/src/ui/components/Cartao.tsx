import type { ReactNode } from 'react'

import estilos from './Cartao.module.css'
import { Dica } from './Dica'

interface Propriedades {
  titulo: string
  ajuda?: string
  nota?: string
  leitura?: ReactNode
  children: ReactNode
}

export function Cartao({ titulo, ajuda, nota, leitura, children }: Propriedades) {
  return (
    <section className={estilos.cartao}>
      <h3 className={estilos.titulo}>
        {titulo}
        {ajuda && <Dica texto={ajuda} />}
      </h3>
      <div className={estilos.conteudo}>{children}</div>
      {leitura && <p className={estilos.leitura}>{leitura}</p>}
      {nota && <p className={estilos.nota}>{nota}</p>}
    </section>
  )
}
