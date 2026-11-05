import { useMemo } from 'react'

import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import { classeDoValor, faixasIguais } from '../../../../domain/classes'
import { temTerritorio } from '../../../../domain/filtros'
import { formatarNumero, formatarNumeroOpcional } from '../../../../domain/formatacao'
import {
  CHAVES_DOS_CRITERIOS,
  NOTA_MAXIMA,
  type BairroPriorizado,
  type Criterio,
  type Prioridade,
} from '../../../../domain/prioridade'
import { BarrasEmpilhadas } from '../../../charts/BarrasEmpilhadas'
import { Cartao } from '../../../components/Cartao'
import { Colunas } from '../../../components/Secao'
import { LegendaDoMapa } from '../../../map/LegendaDoMapa'
import { MapaCoropletico, type ValorDoBairro } from '../../../map/MapaCoropletico'
import { CORES_DOS_CRITERIOS } from './cores'

const BAIRROS_NA_LISTA = 15
const FAIXAS = faixasIguais(NOTA_MAXIMA)

function dicaDoBairro(bairro: BairroPriorizado, criterios: readonly Criterio[]): string {
  const detalhes = criterios.map(
    (criterio) =>
      `${criterio.nome}: ${formatarNumeroOpcional(bairro[criterio.chave], 1)} ${criterio.unidade}`,
  )
  return [
    `${bairro.nome} (${bairro.posicao}º)`,
    `Índice: ${formatarNumero(bairro.indice, 1)}`,
    ...detalhes,
  ].join('\n')
}

interface Propriedades {
  prioridade: Prioridade
  criterios: readonly Criterio[]
}

export function IndiceDosBairros({ prioridade, criterios }: Propriedades) {
  const { filtros } = useFiltrosGlobais()
  const emDestaque = (bairro: BairroPriorizado) =>
    (filtros.rpas.length === 0 || filtros.rpas.includes(bairro.rpa)) &&
    (filtros.bairros.length === 0 || filtros.bairros.includes(bairro.bairroOficial))
  const valores = useMemo(() => {
    const mapa = new Map<string, ValorDoBairro>()
    prioridade.bairros.forEach((bairro) => {
      const dentro =
        (filtros.rpas.length === 0 || filtros.rpas.includes(bairro.rpa)) &&
        (filtros.bairros.length === 0 || filtros.bairros.includes(bairro.bairroOficial))
      mapa.set(bairro.nome, {
        classe: classeDoValor(bairro.indice, FAIXAS),
        emDestaque: dentro,
        dica: dicaDoBairro(bairro, criterios),
      })
    })
    return mapa
  }, [prioridade.bairros, criterios, filtros.rpas, filtros.bairros])
  const lista = prioridade.bairros.filter(emDestaque).slice(0, BAIRROS_NA_LISTA)
  const titulo = `Os 15 bairros com maior índice${temTerritorio(filtros) ? ' no recorte' : ''}`

  return (
    <Colunas>
      <Cartao
        titulo="Índice de prioridade por bairro"
        leitura="Quanto mais escuro, maior a prioridade. Hachurado: bairros com menos de 1.000 moradores, fora do índice."
      >
        <MapaCoropletico
          rotulo="Índice de prioridade por bairro do Recife. Os 15 maiores estão na lista ao lado."
          valores={valores}
          altura={500}
        />
        <LegendaDoMapa titulo="índice de prioridade (0 a 10)" faixas={FAIXAS} casas={0} />
      </Cartao>
      <Cartao
        titulo={titulo}
        ajuda="Cada barra é a nota do bairro; as cores mostram quantos pontos vieram de cada critério."
        leitura="Barras mais longas, prioridade maior. A cor mostra o porquê: um bairro pode subir por risco, por vulnerabilidade, por pedidos que passaram do prazo ou por problemas que voltam."
      >
        <BarrasEmpilhadas
          dados={lista.map((bairro) => ({
            rotulo: `${bairro.posicao}º ${bairro.nome}`,
            ...bairro.contribuicoes,
          }))}
          eixo="rotulo"
          orientacao="horizontal"
          maximo={NOTA_MAXIMA}
          larguraDoRotulo={190}
          formatar={(valor) => formatarNumero(valor, 1)}
          segmentos={CHAVES_DOS_CRITERIOS.map((chave) => ({
            chave,
            rotulo: criterios.find((criterio) => criterio.chave === chave)?.nome ?? chave,
            cor: CORES_DOS_CRITERIOS[chave],
          }))}
        />
      </Cartao>
    </Colunas>
  )
}
