import { useId, useState, type FormEvent } from 'react'

import {
  rotuloDaResposta,
  TAMANHO_MAXIMO_DA_RESPOSTA_AO_CIDADAO,
  type RespostaAoEncaminhamento,
  type RespostaPossivel,
  type SituacaoDoEncaminhamento,
} from '../../../domain/encaminhamentos'
import { isoDaData } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Encaminhamentos.module.css'

const TAMANHO_MAXIMO_DA_OBSERVACAO = 280
const TAMANHO_MAXIMO_DO_PROTOCOLO = 40

interface Propriedades {
  respostas: readonly RespostaPossivel[]
  situacaoAtual: SituacaoDoEncaminhamento
  rotuloDoBotao: string
  aoResponder: (resposta: RespostaAoEncaminhamento) => Promise<void>
}

export function FormularioDeRetorno({
  respostas,
  situacaoAtual,
  rotuloDoBotao,
  aoResponder,
}: Propriedades) {
  const id = useId()
  const [situacao, definirSituacao] = useState<RespostaPossivel | null>(null)
  const [protocoloDoOrgao, definirProtocolo] = useState('')
  const [observacao, definirObservacao] = useState('')
  const [respostaAoCidadao, definirResposta] = useState('')
  const [previsao, definirPrevisao] = useState('')
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!situacao) return
    definirEnviando(true)
    definirFalha(null)
    try {
      await aoResponder({
        situacao,
        protocoloDoOrgao,
        observacao,
        respostaAoCidadao,
        previsao: previsao || null,
      })
      definirSituacao(null)
      definirObservacao('')
      definirResposta('')
      definirPrevisao('')
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
            {rotuloDaResposta(resposta, situacaoAtual)}
          </label>
        ))}
      </fieldset>
      {situacao === 'recebido' && (
        <div className={estilos.campo}>
          <label htmlFor={`${id}-previsao`}>Previsão de conclusão (opcional)</label>
          <input
            id={`${id}-previsao`}
            type="date"
            min={isoDaData(new Date())}
            value={previsao}
            onChange={(evento) => definirPrevisao(evento.target.value)}
          />
        </div>
      )}
      <div className={estilos.campo}>
        <label htmlFor={`${id}-resposta`}>Resposta para quem fez o pedido (opcional)</label>
        <textarea
          id={`${id}-resposta`}
          value={respostaAoCidadao}
          maxLength={TAMANHO_MAXIMO_DA_RESPOSTA_AO_CIDADAO}
          onChange={(evento) => definirResposta(evento.target.value)}
          aria-describedby={`${id}-dica-resposta`}
        />
        <p id={`${id}-dica-resposta`} className={estilos.nota}>
          Até 500 caracteres. Vai para quem acompanha o pedido, no sino e por e-mail. Sem nome, CPF,
          telefone ou endereço completo.
        </p>
      </div>
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
        <label htmlFor={`${id}-observacao`}>Nota interna (opcional)</label>
        <textarea
          id={`${id}-observacao`}
          value={observacao}
          maxLength={TAMANHO_MAXIMO_DA_OBSERVACAO}
          onChange={(evento) => definirObservacao(evento.target.value)}
          aria-describedby={`${id}-dica`}
        />
        <p id={`${id}-dica`} className={estilos.nota}>
          Até 280 caracteres, sem CPF, telefone ou e-mail. Só a gestão e o órgão veem a nota.
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
