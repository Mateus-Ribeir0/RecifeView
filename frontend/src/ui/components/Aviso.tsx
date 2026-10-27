import type { ReactNode, Ref } from 'react'

import estilos from './Aviso.module.css'

type TipoDeAviso = 'erro' | 'alerta' | 'info' | 'sucesso'

interface Propriedades {
  tipo: TipoDeAviso
  titulo?: string
  children: ReactNode
  ref?: Ref<HTMLDivElement>
}

export function Aviso({ tipo, titulo, children, ref }: Propriedades) {
  return (
    <div
      ref={ref}
      tabIndex={-1}
      role={tipo === 'erro' ? 'alert' : 'status'}
      className={`${estilos.aviso} ${estilos[tipo]}`}
    >
      {titulo && <p className={estilos.titulo}>{titulo}</p>}
      <div>{children}</div>
    </div>
  )
}
