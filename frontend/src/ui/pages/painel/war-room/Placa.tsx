import type { ReactNode } from 'react'

import estilos from './PaginaWarRoom.module.css'

interface Propriedades {
  rotulo: string
  valor: string
  ajuda: string
  alerta?: boolean
  children: ReactNode
}

export function Placa({ rotulo, valor, ajuda, alerta, children }: Propriedades) {
  return (
    <div className={`${estilos.placa} ${alerta ? estilos.placaEmAlerta : ''}`} title={ajuda}>
      <p className={estilos.rotuloDaPlaca}>
        {rotulo}
        {alerta && <span className="visualmente-oculto"> (atenção)</span>}
      </p>
      <p className={`${estilos.valorDaPlaca} numero`}>{valor}</p>
      <p className={estilos.detalheDaPlaca}>{children}</p>
    </div>
  )
}
