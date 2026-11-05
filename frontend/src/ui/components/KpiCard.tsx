import { Dica } from './Dica'
import estilos from './KpiCard.module.css'

interface Propriedades {
  rotulo: string
  valor: string
  contexto?: string
  ajuda?: string
  alerta?: boolean
}

export function KpiCard({ rotulo, valor, contexto, ajuda, alerta }: Propriedades) {
  return (
    <div className={`${estilos.kpi} ${alerta ? estilos.alerta : ''}`}>
      <p className={estilos.rotulo}>
        {rotulo}
        {ajuda && <Dica texto={ajuda} />}
      </p>
      <p className={`${estilos.valor} numero`}>{valor}</p>
      {contexto && <p className={estilos.contexto}>{contexto}</p>}
    </div>
  )
}
