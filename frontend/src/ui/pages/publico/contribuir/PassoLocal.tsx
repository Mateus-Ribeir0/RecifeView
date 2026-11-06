import { Suspense, use, useId } from 'react'

import { useLogradourosDoBairro } from '../../../../application/contribuicoes/useFormulario'
import {
  chaveDoNome,
  type BairroDoFormulario,
  type ErrosDoRelato,
  type RascunhoDoRelato,
} from '../../../../domain/contribuicoes'
import campo from '../../../components/Campo.module.css'
import { CampoDeTexto } from '../../../components/CampoDeTexto'
import { carregarBairros } from '../../../map/carregarBairros'
import { MapaDosBairros } from '../../../map/MapaDosBairros'
import estilos from './PassoLocal.module.css'

function MapaDoBairro({ nome }: { nome: string }) {
  const bairros = use(carregarBairros())
  const bairro = bairros.find((item) => chaveDoNome(item.nome) === chaveDoNome(nome))
  return (
    <MapaDosBairros
      tom="claro"
      descricao={nome ? `Mapa do Recife com o bairro ${nome} em destaque` : 'Mapa do Recife'}
      bairroEmFoco={bairro?.codigo ?? null}
    />
  )
}

interface Propriedades {
  bairros: readonly BairroDoFormulario[]
  rascunho: RascunhoDoRelato
  erros: ErrosDoRelato
  aoMudar: (mudancas: Partial<RascunhoDoRelato>) => void
}

export function PassoLocal({ bairros, rascunho, erros, aoMudar }: Propriedades) {
  const idDoBairro = useId()
  const idDasVias = useId()
  const vias = useLogradourosDoBairro(rascunho.bairroOficial)
  const bairro = bairros.find(({ chave }) => chave === rascunho.bairroOficial)

  return (
    <>
      <div>
        <h2 className={estilos.pergunta}>Onde é o problema?</h2>
        <p className={estilos.ajuda}>
          O endereço do problema, não o seu. Ele é usado só para conferir se já existe outro relato.
        </p>
      </div>
      <div className={estilos.grade}>
        <div className={estilos.campos}>
          <div className={campo.campo}>
            <label htmlFor={idDoBairro} className={campo.rotulo}>
              Bairro
            </label>
            <select
              id={idDoBairro}
              className={campo.entrada}
              value={rascunho.bairroOficial}
              aria-invalid={erros.bairro ? true : undefined}
              onChange={(evento) => aoMudar({ bairroOficial: evento.target.value })}
            >
              <option value="">Escolha o bairro</option>
              {bairros.map(({ chave, nome }) => (
                <option key={chave} value={chave}>
                  {nome}
                </option>
              ))}
            </select>
            {erros.bairro && <p className={campo.erro}>{erros.bairro}</p>}
          </div>
          <CampoDeTexto
            rotulo="Rua"
            dica="Comece a digitar: as ruas do bairro aparecem como sugestão."
            list={idDasVias}
            autoComplete="off"
            maxLength={120}
            value={rascunho.logradouro}
            erro={erros.logradouro}
            onChange={(evento) => aoMudar({ logradouro: evento.target.value })}
          />
          <datalist id={idDasVias}>
            {vias.map((via) => (
              <option key={via} value={via} />
            ))}
          </datalist>
          <CampoDeTexto
            rotulo="Número mais próximo (opcional)"
            dica="Sem número, a gestão confere com mais cuidado se é o mesmo lugar."
            inputMode="numeric"
            autoComplete="off"
            maxLength={10}
            value={rascunho.numero}
            erro={erros.numero}
            onChange={(evento) => aoMudar({ numero: evento.target.value })}
          />
        </div>
        <figure className={estilos.mapa}>
          <Suspense fallback={<div className={estilos.reservaDoMapa} />}>
            <MapaDoBairro nome={bairro?.nome ?? ''} />
          </Suspense>
          <figcaption>
            {bairro ? `${bairro.nome}, RPA ${bairro.rpa}` : 'Os 94 bairros do Recife'}
          </figcaption>
        </figure>
      </div>
    </>
  )
}
