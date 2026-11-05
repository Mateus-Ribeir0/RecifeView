import { useMemo, useState } from 'react'

import { FiltroSuspenso } from './FiltroSuspenso'
import { resumirEscolha, type OpcaoDoSeletor } from './resumirEscolha'
import estilos from './SeletorMultiplo.module.css'

interface PropriedadesDaLista {
  rotulo: string
  opcoes: readonly OpcaoDoSeletor[]
  selecionados: readonly string[]
  aoMudar: (selecionados: string[]) => void
}

interface Propriedades extends PropriedadesDaLista {
  nenhum: string
}

const OPCOES_PARA_BUSCA = 8

function semAcento(texto: string): string {
  return texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

export function ListaDeOpcoes({ rotulo, opcoes, selecionados, aoMudar }: PropriedadesDaLista) {
  const [busca, definirBusca] = useState('')
  const visiveis = useMemo(() => {
    const termo = semAcento(busca)
    return opcoes.filter((opcao) => semAcento(opcao.rotulo).includes(termo))
  }, [opcoes, busca])

  function alternar(valor: string) {
    aoMudar(
      selecionados.includes(valor)
        ? selecionados.filter((item) => item !== valor)
        : [...selecionados, valor],
    )
  }

  return (
    <div className={estilos.lista}>
      {opcoes.length > OPCOES_PARA_BUSCA && (
        <input
          type="search"
          className={estilos.busca}
          placeholder="Buscar"
          aria-label={`Buscar em ${rotulo}`}
          value={busca}
          onChange={(evento) => definirBusca(evento.target.value)}
        />
      )}
      <ul>
        {visiveis.map((opcao) => (
          <li key={opcao.valor}>
            <label className={estilos.opcao}>
              <input
                type="checkbox"
                checked={selecionados.includes(opcao.valor)}
                onChange={() => alternar(opcao.valor)}
              />
              {opcao.rotulo}
            </label>
          </li>
        ))}
        {visiveis.length === 0 && <li className={estilos.semOpcao}>Nada encontrado</li>}
      </ul>
    </div>
  )
}

export function SeletorMultiplo({ rotulo, nenhum, opcoes, selecionados, aoMudar }: Propriedades) {
  return (
    <FiltroSuspenso
      rotulo={rotulo}
      valor={resumirEscolha(selecionados, opcoes, nenhum)}
      ativo={selecionados.length > 0}
    >
      <ListaDeOpcoes
        rotulo={rotulo}
        opcoes={opcoes}
        selecionados={selecionados}
        aoMudar={aoMudar}
      />
    </FiltroSuspenso>
  )
}
