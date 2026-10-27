import { use, useMemo } from 'react'

import type { Bairro, NumeroDaRpa } from '../../domain/territorio'
import { carregarBairros } from './carregarBairros'
import estilos from './MapaDosBairros.module.css'
import { projetarBairros } from './projecao'

const LARGURA_DO_DESENHO = 600

interface Propriedades {
  tom: 'claro' | 'sobreAzul'
  descricao: string
  rpaEmDestaque?: NumeroDaRpa | null
  bairroEmFoco?: number | null
  aoFocarBairro?: (bairro: Bairro | null) => void
}

export function MapaDosBairros({
  tom,
  descricao,
  rpaEmDestaque = null,
  bairroEmFoco = null,
  aoFocarBairro,
}: Propriedades) {
  const bairros = use(carregarBairros())
  const mapa = useMemo(() => projetarBairros(bairros, LARGURA_DO_DESENHO), [bairros])

  return (
    <svg
      viewBox={`0 0 ${mapa.largura} ${mapa.altura}`}
      role="img"
      aria-label={descricao}
      className={`${estilos.mapa} ${estilos[tom]}`}
    >
      {mapa.bairros.map(({ bairro, caminho }) => (
        <path
          key={bairro.codigo}
          d={caminho}
          className={estilos.bairro}
          data-destaque={rpaEmDestaque === bairro.rpa || undefined}
          data-foco={bairroEmFoco === bairro.codigo || undefined}
          onPointerEnter={aoFocarBairro && (() => aoFocarBairro(bairro))}
          onPointerLeave={aoFocarBairro && (() => aoFocarBairro(null))}
        />
      ))}
    </svg>
  )
}
