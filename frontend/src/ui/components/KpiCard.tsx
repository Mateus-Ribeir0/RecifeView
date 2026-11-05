import type { ReactNode } from 'react'
import { Link } from 'react-router'

import { Dica } from './Dica'
import { Icone } from './Icone'
import estilos from './KpiCard.module.css'

interface Propriedades {
  rotulo: string
  valor: string
  contexto?: string
  ajuda?: string
  alerta?: boolean
  visual?: ReactNode
  para?: string
}

export function KpiCard({ rotulo, valor, contexto, ajuda, alerta, visual, para }: Propriedades) {
  return (
    <div className={estilos.kpi}>
      <p className={estilos.rotulo}>
        {alerta && (
          <span className={estilos.marcaDeAlerta}>
            <Icone nome="alerta" tamanho={14} />
            <span className="visualmente-oculto">Atenção: </span>
          </span>
        )}
        {para ? (
          <Link to={para} className={estilos.link}>
            {rotulo}
          </Link>
        ) : (
          rotulo
        )}
        {ajuda && <Dica texto={ajuda} />}
      </p>
      <p className={`${estilos.valor} numero`}>{valor}</p>
      <p className={estilos.contexto}>{contexto}</p>
      <div className={estilos.visual}>{visual}</div>
    </div>
  )
}
