import type { ReactNode } from 'react'

import estilos from './Importacoes.module.css'

export interface OpcaoDaPergunta {
  valor: string
  rotulo: string
  detalhe?: string
}

interface Propriedades {
  titulo: string
  nome: string
  opcoes: readonly OpcaoDaPergunta[]
  valor: string | undefined
  aoEscolher: (valor: string) => void
  children?: ReactNode
}

export function PerguntaDeEscolha({
  titulo,
  nome,
  opcoes,
  valor,
  aoEscolher,
  children,
}: Propriedades) {
  return (
    <fieldset className={estilos.pergunta}>
      <legend>{titulo}</legend>
      {children}
      {opcoes.map((opcao) => (
        <label key={opcao.valor} className={estilos.opcaoDaPergunta}>
          <input
            type="radio"
            name={nome}
            checked={valor === opcao.valor}
            onChange={() => aoEscolher(opcao.valor)}
          />
          <span>
            {opcao.rotulo}
            {opcao.detalhe && <small>{opcao.detalhe}</small>}
          </span>
        </label>
      ))}
    </fieldset>
  )
}
