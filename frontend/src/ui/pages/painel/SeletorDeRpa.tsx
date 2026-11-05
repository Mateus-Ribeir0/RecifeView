import { Suspense } from 'react'

import { RPAS } from '../../../domain/territorio'
import { MapaDasRpas } from '../../map/MapaDasRpas'
import { FiltroSuspenso } from './FiltroSuspenso'
import { resumirEscolha } from './resumirEscolha'
import estilos from './SeletorDeRpa.module.css'
import { ListaDeOpcoes } from './SeletorMultiplo'

interface Propriedades {
  rpas: readonly string[]
  selecionadas: readonly string[]
  aoMudar: (selecionadas: string[]) => void
}

function rotuloDaRpa(rpa: string): string {
  const nome = RPAS.find((item) => String(item.numero) === rpa)?.nome
  return nome ? `RPA ${rpa} (${nome})` : `RPA ${rpa}`
}

export function SeletorDeRpa({ rpas, selecionadas, aoMudar }: Propriedades) {
  const opcoes = rpas.map((rpa) => ({ valor: rpa, rotulo: rotuloDaRpa(rpa) }))

  function alternar(rpa: string) {
    aoMudar(
      selecionadas.includes(rpa)
        ? selecionadas.filter((item) => item !== rpa)
        : [...selecionadas, rpa],
    )
  }

  return (
    <FiltroSuspenso
      rotulo="RPA"
      valor={resumirEscolha(selecionadas, opcoes, 'Todas')}
      ativo={selecionadas.length > 0}
    >
      <div className={estilos.seletor}>
        <Suspense fallback={null}>
          <MapaDasRpas selecionadas={selecionadas} aoAlternar={alternar} />
        </Suspense>
        <ListaDeOpcoes rotulo="RPA" opcoes={opcoes} selecionados={selecionadas} aoMudar={aoMudar} />
      </div>
    </FiltroSuspenso>
  )
}
