import { use, useMemo } from 'react'

import { chaveDoNome } from '../../domain/contribuicoes'
import { carregarBairros } from './carregarBairros'
import estilos from './MapaDeEscolhaDoBairro.module.css'
import { projetarBairros } from './projecao'

const LARGURA_DO_DESENHO = 600
const DESCRICAO_PADRAO =
  'Mapa do Recife. Bairros com relato em destaque. Use a lista de bairros para escolher pelo teclado.'

interface Propriedades {
  marcados: ReadonlySet<string>
  escolhido: string
  aoEscolher: (bairro: string) => void
  descricao?: string
}

/** Marca só quem tem relato, sem graduar: cor graduada seria lida como quantidade. */
export function MapaDeEscolhaDoBairro({
  marcados,
  escolhido,
  aoEscolher,
  descricao = DESCRICAO_PADRAO,
}: Propriedades) {
  const bairros = use(carregarBairros())
  const mapa = useMemo(() => projetarBairros(bairros, LARGURA_DO_DESENHO), [bairros])

  return (
    <svg
      viewBox={`0 0 ${mapa.largura} ${mapa.altura}`}
      className={estilos.mapa}
      role="img"
      aria-label={descricao}
    >
      {mapa.bairros.map(({ bairro, caminho }) => {
        const chave = chaveDoNome(bairro.nome)
        return (
          <path
            key={bairro.codigo}
            d={caminho}
            className={estilos.bairro}
            data-com-relato={marcados.has(chave) || undefined}
            data-escolhido={escolhido === chave || undefined}
            onClick={() => aoEscolher(escolhido === chave ? '' : chave)}
          >
            <title>{bairro.nome}</title>
          </path>
        )
      })}
    </svg>
  )
}
