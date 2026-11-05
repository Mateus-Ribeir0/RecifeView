import type { ReactNode } from 'react'

import estilos from './Cartao.module.css'
import { Dica } from './Dica'

interface Propriedades {
  titulo: string
  ajuda?: string
  nota?: string
  leitura?: ReactNode
  acao?: ReactNode
  children: ReactNode
}

export function Cartao({ titulo, ajuda, nota, leitura, acao, children }: Propriedades) {
  return (
    <section className={estilos.cartao}>
      <div className={estilos.topo}>
        <h3 className={estilos.titulo}>
          {titulo}
          {ajuda && <Dica texto={ajuda} />}
        </h3>
        {acao}
      </div>
      <div className={estilos.conteudo}>{children}</div>
      {(leitura || nota) && (
        <div className={estilos.rodape}>
          {leitura && (
            <details className={estilos.leitura}>
              <summary>Como ler</summary>
              <p>{leitura}</p>
            </details>
          )}
          {nota && <p className={estilos.nota}>{nota}</p>}
        </div>
      )}
    </section>
  )
}
