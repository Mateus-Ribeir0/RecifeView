import { Dica } from './Dica'
import estilos from './Alternador.module.css'

interface Propriedades {
  rotulo: string
  ajuda: string
  ligado: boolean
  aoMudar: (ligado: boolean) => void
}

export function Alternador({ rotulo, ajuda, ligado, aoMudar }: Propriedades) {
  return (
    <div className={estilos.linha}>
      <label className={estilos.alternador}>
        <input
          type="checkbox"
          role="switch"
          checked={ligado}
          onChange={(evento) => aoMudar(evento.target.checked)}
        />
        <span className={estilos.trilho} aria-hidden="true" />
        {rotulo}
      </label>
      <Dica texto={ajuda} />
    </div>
  )
}
