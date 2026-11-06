import { useId } from 'react'

import {
  OPCOES_DE_RETORNO,
  TAMANHO_MAXIMO_DO_DETALHE,
  type ErrosDoRelato,
  type RascunhoDoRelato,
} from '../../../../domain/contribuicoes'
import campo from '../../../components/Campo.module.css'
import estilos from './PassoEnvio.module.css'

interface Propriedades {
  rascunho: RascunhoDoRelato
  erros: ErrosDoRelato
  aoMudar: (mudancas: Partial<RascunhoDoRelato>) => void
}

export function PassoEnvio({ rascunho, erros, aoMudar }: Propriedades) {
  const idDoDetalhe = useId()

  return (
    <>
      <div>
        <h2 className={estilos.pergunta}>Falta pouco</h2>
        <p className={estilos.ajuda}>Essas respostas mostram onde o atendimento se perde.</p>
      </div>
      <fieldset className={estilos.grupo}>
        <legend className={campo.rotulo}>Você já registrou este problema na Prefeitura?</legend>
        {OPCOES_DE_RETORNO.map(({ valor, rotulo }) => (
          <label key={valor} className={estilos.opcao}>
            <input
              type="radio"
              name="retorno"
              checked={rascunho.retorno === valor}
              onChange={() => aoMudar({ retorno: valor })}
            />
            {rotulo}
          </label>
        ))}
      </fieldset>
      <div className={campo.campo}>
        <label htmlFor={idDoDetalhe} className={campo.rotulo}>
          Ponto de referência ou detalhe (opcional)
        </label>
        <p className={campo.dica}>
          Não escreva nomes, telefone, CPF ou e-mail. Este texto é apagado em 90 dias.
        </p>
        <textarea
          id={idDoDetalhe}
          className={`${campo.entrada} ${estilos.texto}`}
          rows={3}
          maxLength={TAMANHO_MAXIMO_DO_DETALHE}
          value={rascunho.detalhe}
          aria-invalid={erros.detalhe ? true : undefined}
          onChange={(evento) => aoMudar({ detalhe: evento.target.value })}
        />
        <p className={`numero ${estilos.contagem}`}>
          {rascunho.detalhe.length} de {TAMANHO_MAXIMO_DO_DETALHE}
        </p>
        {erros.detalhe && <p className={campo.erro}>{erros.detalhe}</p>}
      </div>
      <label className={estilos.ciente}>
        <input
          type="checkbox"
          checked={rascunho.ciente}
          aria-invalid={erros.ciente ? true : undefined}
          onChange={(evento) => aoMudar({ ciente: evento.target.checked })}
        />
        <span>
          Entendi que este relato alimenta a análise da gestão, não é um canal oficial de
          atendimento, não gera protocolo e não substitui a Central 156.
        </span>
      </label>
      {erros.ciente && <p className={campo.erro}>{erros.ciente}</p>}
    </>
  )
}
