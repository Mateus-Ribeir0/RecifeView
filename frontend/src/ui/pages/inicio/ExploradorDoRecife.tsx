import { Suspense, use, useState } from 'react'

import { RPAS, type Bairro, type NumeroDaRpa } from '../../../domain/territorio'
import { carregarBairros } from '../../map/carregarBairros'
import { MapaDosBairros } from '../../map/MapaDosBairros'
import estilos from './ExploradorDoRecife.module.css'

const DESCRICAO_DO_MAPA =
  'Mapa dos 94 bairros do Recife, agrupados em 6 regiões político-administrativas (RPAs)'

function nomeDaRpa(numero: NumeroDaRpa): string {
  return RPAS.find((rpa) => rpa.numero === numero)?.nome ?? ''
}

interface Selecao {
  rpa: NumeroDaRpa | null
  bairro: Bairro | null
}

function LeituraDaSelecao({ rpa, bairro }: Selecao) {
  const bairros = use(carregarBairros())
  if (bairro) {
    return (
      <>
        <strong>{bairro.nome}</strong>, na RPA {bairro.rpa} ({nomeDaRpa(bairro.rpa)})
      </>
    )
  }
  if (rpa) {
    const quantidade = bairros.filter((candidato) => candidato.rpa === rpa).length
    return (
      <>
        <strong>
          RPA {rpa}, {nomeDaRpa(rpa)}
        </strong>
        : {quantidade} bairros
      </>
    )
  }
  return <>Passe o mouse sobre um bairro ou escolha uma RPA.</>
}

export function ExploradorDoRecife() {
  const [rpa, definirRpa] = useState<NumeroDaRpa | null>(null)
  const [bairro, definirBairro] = useState<Bairro | null>(null)

  return (
    <figure className={estilos.explorador}>
      <div className={estilos.moldura}>
        <Suspense fallback={<div className={estilos.reserva} />}>
          <MapaDosBairros
            tom="claro"
            descricao={DESCRICAO_DO_MAPA}
            rpaEmDestaque={rpa}
            bairroEmFoco={bairro?.codigo ?? null}
            aoFocarBairro={definirBairro}
          />
        </Suspense>
      </div>
      <figcaption className={estilos.legenda}>
        <p className={estilos.leitura} aria-live="polite">
          <Suspense fallback="Carregando os bairros...">
            <LeituraDaSelecao rpa={rpa} bairro={bairro} />
          </Suspense>
        </p>
        <div className={estilos.rpas} role="group" aria-label="Destacar uma RPA no mapa">
          {RPAS.map(({ numero, nome }) => (
            <button
              key={numero}
              type="button"
              className={estilos.rpa}
              aria-pressed={rpa === numero}
              onClick={() => definirRpa((atual) => (atual === numero ? null : numero))}
            >
              RPA {numero} <span>{nome}</span>
            </button>
          ))}
        </div>
        <p className={estilos.fonte}>
          Malha de bairros: Prefeitura do Recife, Portal de Dados Abertos (licença ODbL).
        </p>
      </figcaption>
    </figure>
  )
}
