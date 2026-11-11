import { useId, useState, type FormEvent } from 'react'

import {
  ROTULOS_DAS_RESPOSTAS,
  type RespostaAoEncaminhamento,
  type RespostaPossivel,
} from '../../../domain/encaminhamentos'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Encaminhamentos.module.css'

const TAMANHO_MAXIMO_DA_OBSERVACAO = 280
const TAMANHO_MAXIMO_DO_PROTOCOLO = 40

interface Propriedades {
  respostas: readonly RespostaPossivel[]
  rotuloDoBotao: string
  aoResponder: (resposta: RespostaAoEncaminhamento) => Promise<void>
}

export function FormularioDeRetorno({ respostas, rotuloDoBotao, aoResponder }: Propriedades) {
  const id = useId()
  const [situacao, definirSituacao] = useState<RespostaPossivel | null>(null)
  const [protocoloDoOrgao, definirProtocolo] = useState('')
  const [observacao, definirObservacao] = useState('')
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!situacao) return
    definirEnviando(true)
    definirFalha(null)
    try {
      await aoResponder({ situacao, protocoloDoOrgao, observacao })
      definirSituacao(null)
      definirObservacao('')
    } catch (motivo) {
      definirFalha(motivo)
    } finally {
      definirEnviando(false)
    }
  }

  return (
    <form onSubmit={(evento) => void enviar(evento)} className={estilos.formulario}>
      <fieldset className={estilos.campo}>
        <legend>O que aconteceu</legend>
        {respostas.map((resposta) => (
          <label key={resposta} className={estilos.marcacao}>
            <input
              type="radio"
              name={`${id}-situacao`}
              checked={situacao === resposta}
              onChange={() => definirSituacao(resposta)}
            />
            {ROTULOS_DAS_RESPOSTAS[resposta]}
          </label>
        ))}
      </fieldset>
      <div className={estilos.campo}>
        <label htmlFor={`${id}-protocolo`}>Protocolo no órgão (opcional)</label>
        <input
          id={`${id}-protocolo`}
          value={protocoloDoOrgao}
          maxLength={TAMANHO_MAXIMO_DO_PROTOCOLO}
          onChange={(evento) => definirProtocolo(evento.target.value)}
        />
      </div>
      <div className={estilos.campo}>
        <label htmlFor={`${id}-observacao`}>Observação (opcional)</label>
        <textarea
          id={`${id}-observacao`}
          value={observacao}
          maxLength={TAMANHO_MAXIMO_DA_OBSERVACAO}
          onChange={(evento) => definirObservacao(evento.target.value)}
          aria-describedby={`${id}-dica`}
        />
        <p id={`${id}-dica`} className={estilos.nota}>
          Até 280 caracteres, sem CPF, telefone ou e-mail. A gestão vê a observação; quem fez o
          pedido vê só a etapa e o protocolo do órgão.
        </p>
      </div>
      {falha !== null && (
        <Aviso tipo="erro" titulo="Não foi possível registrar">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
      <div className={estilos.acoes}>
        <Botao type="submit" disabled={!situacao || enviando}>
          {enviando ? 'Registrando...' : rotuloDoBotao}
        </Botao>
      </div>
    </form>
  )
}
