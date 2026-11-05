import { use, useMemo } from 'react'

import { carregarBairros } from './carregarBairros'
import estilos from './MapaDasRpas.module.css'
import { projetarBairros } from './projecao'

const LARGURA_DO_DESENHO = 300

interface Propriedades {
  selecionadas: readonly string[]
  aoAlternar: (rpa: string) => void
}

export function MapaDasRpas({ selecionadas, aoAlternar }: Propriedades) {
  const bairros = use(carregarBairros())
  const mapa = useMemo(() => projetarBairros(bairros, LARGURA_DO_DESENHO), [bairros])

  return (
    <svg
      viewBox={`0 0 ${mapa.largura} ${mapa.altura}`}
      className={estilos.mapa}
      aria-hidden="true"
      data-com-escolha={selecionadas.length > 0 || undefined}
    >
      {mapa.bairros.map(({ bairro, caminho }) => (
        <path
          key={bairro.codigo}
          d={caminho}
          className={estilos.bairro}
          data-rpa={bairro.rpa}
          data-ativa={selecionadas.includes(String(bairro.rpa)) || undefined}
          onClick={() => aoAlternar(String(bairro.rpa))}
        >
          <title>RPA {bairro.rpa}</title>
        </path>
      ))}
    </svg>
  )
}
