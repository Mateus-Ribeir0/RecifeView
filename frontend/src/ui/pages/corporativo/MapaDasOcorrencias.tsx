import { useMemo } from 'react'

import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import { classeDaContagem, faixasDaContagem } from '../../../domain/classes'
import type { ContagemPorRotulo } from '../../../domain/corporativo'
import { contar } from '../../../domain/formatacao'
import { LegendaDaContagem } from '../../map/LegendaDaContagem'
import { MapaCoropletico, type ValorDoBairro } from '../../map/MapaCoropletico'

interface Propriedades {
  rotulo: string
  contagens: readonly ContagemPorRotulo[]
  unidade: readonly [singular: string, plural: string]
  aoClicar?: (bairroOficial: string) => void
}

function comInicialMaiuscula(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

/** Todos os bairros entram: o que não tem registro aparece como zero, e não como sem dado. */
export function MapaDasOcorrencias({ rotulo, contagens, unidade, aoClicar }: Propriedades) {
  const { catalogo } = useCatalogoDoFormulario()
  const maximo = Math.max(0, ...contagens.map((item) => item.quantidade))
  const valores = useMemo(() => {
    const porBairro = new Map(contagens.map((item) => [item.rotulo, item.quantidade]))
    const mapa = new Map<string, ValorDoBairro>()
    catalogo?.bairros.forEach((bairro) => {
      const quantidade = porBairro.get(bairro.chave) ?? 0
      mapa.set(bairro.nome, {
        classe: classeDaContagem(quantidade, maximo),
        emDestaque: true,
        dica: `${bairro.nome}\n${contar(quantidade, unidade[0], unidade[1])}`,
      })
    })
    return mapa
  }, [catalogo, contagens, maximo, unidade])
  const chavePeloNome = useMemo(
    () => new Map(catalogo?.bairros.map((bairro) => [bairro.nome, bairro.chave])),
    [catalogo],
  )

  return (
    <>
      <MapaCoropletico
        rotulo={rotulo}
        valores={valores}
        altura={360}
        aoClicar={aoClicar ? (nome) => aoClicar(chavePeloNome.get(nome) ?? nome) : undefined}
      />
      <LegendaDaContagem
        titulo={comInicialMaiuscula(unidade[1])}
        faixas={faixasDaContagem(maximo)}
      />
    </>
  )
}
