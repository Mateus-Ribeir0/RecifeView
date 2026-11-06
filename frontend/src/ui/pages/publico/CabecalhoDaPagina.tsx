import type { ReactNode } from 'react'

import fotoDoRecife from '../../assets/imagens/recife-skyline.jpg'
import estilos from './CabecalhoDaPagina.module.css'

interface Propriedades {
  rotulo: string
  titulo: string
  children: ReactNode
}

export function CabecalhoDaPagina({ rotulo, titulo, children }: Propriedades) {
  return (
    <header className={estilos.cabecalho}>
      <img src={fotoDoRecife} alt="" className={estilos.foto} />
      <div className={`conteudo ${estilos.grade}`}>
        <p className={estilos.rotulo}>{rotulo}</p>
        <h1 className={estilos.titulo}>{titulo}</h1>
        <p className={estilos.descricao}>{children}</p>
      </div>
    </header>
  )
}
