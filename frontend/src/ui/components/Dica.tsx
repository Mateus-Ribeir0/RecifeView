import { useId } from 'react'

import estilos from './Dica.module.css'

interface Propriedades {
  texto: string
}

export function Dica({ texto }: Propriedades) {
  const id = useId()
  return (
    <span className={estilos.dica}>
      <button type="button" className={estilos.gatilho} aria-label="Ajuda" aria-describedby={id}>
        ?
      </button>
      <span id={id} role="tooltip" className={estilos.balao}>
        {texto}
      </span>
    </span>
  )
}
