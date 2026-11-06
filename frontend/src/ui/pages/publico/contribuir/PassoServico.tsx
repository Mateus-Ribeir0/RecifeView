import { useState } from 'react'

import type { TemaDoFormulario } from '../../../../domain/contribuicoes'
import { Icone, type NomeDoIcone } from '../../../components/Icone'
import estilos from './PassoServico.module.css'

const ICONES_DOS_TEMAS: Readonly<Record<string, NomeDoIcone>> = {
  iluminacao: 'lampada',
  limpeza: 'limpeza',
  arvores: 'arvore',
  drenagem: 'gota',
  ruas: 'via',
}

interface Propriedades {
  temas: readonly TemaDoFormulario[]
  escolhido: string
  erro: string | undefined
  aoEscolher: (codigo: string) => void
}

function temaDoServico(temas: readonly TemaDoFormulario[], codigo: string): string | undefined {
  const tema = temas.find(({ servicos }) => servicos.some((item) => item.codigo === codigo))
  return (tema ?? temas[0])?.chave
}

export function PassoServico({ temas, escolhido, erro, aoEscolher }: Propriedades) {
  const [temaAberto, definirTemaAberto] = useState(() => temaDoServico(temas, escolhido))
  const tema = temas.find(({ chave }) => chave === temaAberto)

  return (
    <>
      <div>
        <h2 className={estilos.pergunta}>O que está acontecendo?</h2>
        <p className={estilos.ajuda}>Escolha o tema e o problema que mais se aproxima.</p>
      </div>
      <div className={estilos.temas} role="group" aria-label="Tema do problema">
        {temas.map(({ chave, rotulo }) => (
          <button
            key={chave}
            type="button"
            className={estilos.tema}
            aria-pressed={chave === temaAberto}
            onClick={() => definirTemaAberto(chave)}
          >
            <Icone nome={ICONES_DOS_TEMAS[chave] ?? 'relato'} tamanho={24} />
            {rotulo}
          </button>
        ))}
      </div>
      <fieldset className={estilos.servicos}>
        <legend className="visualmente-oculto">Problema</legend>
        {tema?.servicos.map(({ codigo, rotulo }) => (
          <label key={codigo} className={estilos.servico}>
            <input
              type="radio"
              name="servico"
              checked={escolhido === codigo}
              onChange={() => aoEscolher(codigo)}
            />
            <span>{rotulo}</span>
          </label>
        ))}
      </fieldset>
      {erro && (
        <p className={estilos.erro} role="alert">
          {erro}
        </p>
      )}
    </>
  )
}
