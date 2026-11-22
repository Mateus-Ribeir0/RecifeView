import { useId, useState, type FormEvent } from 'react'

import { useServicoDoOrgao } from '../../../application/corporativo/contexto'
import {
  ACOES_DO_ORGAO,
  mesmoProblemaQueDaParaJuntar,
  type OcorrenciaDoOrgao,
  type RespostaRegistrada,
} from '../../../domain/corporativo'
import {
  precisaExplicarAoCidadao,
  TAMANHO_MAXIMO_DA_RESPOSTA_AO_CIDADAO,
  type RespostaPossivel,
} from '../../../domain/encaminhamentos'
import { contar, formatarNumero, isoDaData } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Corporativo.module.css'
import { JuntarAoMesmoProblema } from './JuntarAoMesmoProblema'

const TAMANHO_MAXIMO_DA_NOTA = 280
const TAMANHO_MAXIMO_DO_PROTOCOLO = 40
const EXPLICACOES: Readonly<Record<RespostaPossivel, string>> = {
  recebido: 'O órgão vai tratar. Se quiser, informe quando deve ficar pronto.',
  resolvido: 'O problema foi resolvido no local.',
  devolvido: 'A ocorrência não é do órgão. A gestão escolhe outro destino.',
}
const PEDIDOS_DE_RESPOSTA: Readonly<Record<RespostaPossivel, string>> = {
  recebido: 'Conte o que vai ser feito (opcional)',
  resolvido: 'Conte o que foi feito',
  devolvido: 'Explique por que não é do órgão',
}

function rotuloDaAcao(resposta: RespostaPossivel, item: OcorrenciaDoOrgao): string {
  if (resposta === 'recebido' && item.situacao === 'recebido') return 'Atualizar o andamento'
  return ACOES_DO_ORGAO[resposta]
}

function QuemFicaSabendo({ pessoas, juntas }: { pessoas: number; juntas: number }) {
  const acompanham = contar(pessoas, 'pessoa que acompanha', 'pessoas que acompanham')
  const outras = contar(juntas, 'outra ocorrência escolhida', 'outras ocorrências escolhidas')
  return (
    <p className={estilos.quemRecebe}>
      Quem fica sabendo: a gestão que encaminhou
      {pessoas > 0 && ` e ${acompanham} o pedido`}
      {juntas > 0 && `, e quem acompanha as ${outras}`}.
    </p>
  )
}

interface Propriedades {
  item: OcorrenciaDoOrgao
  aoResponder: (registrada: RespostaRegistrada) => void
}

export function FormularioDeResposta({ item, aoResponder }: Propriedades) {
  const servico = useServicoDoOrgao()
  const id = useId()
  const juntaveis = mesmoProblemaQueDaParaJuntar(item.mesmoProblema)
  const [situacao, definirSituacao] = useState<RespostaPossivel | null>(null)
  const [respostaAoCidadao, definirResposta] = useState('')
  const [observacao, definirObservacao] = useState('')
  const [protocoloDoOrgao, definirProtocolo] = useState(item.protocoloDoOrgao ?? '')
  const [previsao, definirPrevisao] = useState('')
  const [tambem, definirTambem] = useState<ReadonlySet<number>>(
    () => new Set(juntaveis.filter((parecido) => parecido.certo).map((parecido) => parecido.id)),
  )
  const [tentou, definirTentou] = useState(false)
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)
  const faltaExplicar =
    situacao !== null && precisaExplicarAoCidadao(situacao) && !respostaAoCidadao.trim()

  function alternar(parecido: number) {
    definirTambem((atual) => {
      const proximo = new Set(atual)
      if (proximo.has(parecido)) proximo.delete(parecido)
      else proximo.add(parecido)
      return proximo
    })
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirTentou(true)
    if (!situacao || faltaExplicar) return
    definirEnviando(true)
    definirFalha(null)
    try {
      const tambemEscolhidas = [...tambem]
      const resposta = { situacao, respostaAoCidadao, observacao, protocoloDoOrgao }
      aoResponder(
        await servico.responder(item.id, {
          ...resposta,
          previsao: previsao || null,
          tambem: tambemEscolhidas,
        }),
      )
    } catch (motivo) {
      definirFalha(motivo)
    } finally {
      definirEnviando(false)
    }
  }

  return (
    <form onSubmit={(evento) => void enviar(evento)} className={estilos.formulario} noValidate>
      <fieldset className={estilos.campo}>
        <legend>O que o órgão informa</legend>
        <div className={estilos.escolhas}>
          {item.respostasPossiveis.map((resposta) => (
            <label key={resposta} className={estilos.escolha}>
              <input
                type="radio"
                name={`${id}-situacao`}
                checked={situacao === resposta}
                onChange={() => definirSituacao(resposta)}
              />
              <span>
                <strong>{rotuloDaAcao(resposta, item)}</strong>
                <small>{EXPLICACOES[resposta]}</small>
              </span>
            </label>
          ))}
        </div>
        {tentou && !situacao && <p className={estilos.erroDoCampo}>Escolha uma das opções.</p>}
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

      {situacao && (
        <>
          <div
            className={`${estilos.campo} ${faltaExplicar && tentou ? estilos.campoComErro : ''}`}
          >
            <label htmlFor={`${id}-resposta`}>{PEDIDOS_DE_RESPOSTA[situacao]}</label>
            <textarea
              id={`${id}-resposta`}
              value={respostaAoCidadao}
              maxLength={TAMANHO_MAXIMO_DA_RESPOSTA_AO_CIDADAO}
              onChange={(evento) => definirResposta(evento.target.value)}
              aria-describedby={`${id}-dica-resposta`}
              aria-invalid={faltaExplicar && tentou}
            />
            <p id={`${id}-dica-resposta`} className={estilos.dicaDoCampo}>
              <span>
                Vai para quem acompanha o pedido, no sino e por e-mail. Sem nome, CPF, telefone ou
                endereço completo.
              </span>
              <span className="numero">
                {formatarNumero(respostaAoCidadao.length)}/{TAMANHO_MAXIMO_DA_RESPOSTA_AO_CIDADAO}
              </span>
            </p>
            {faltaExplicar && tentou && (
              <p className={estilos.erroDoCampo}>Escreva a resposta para quem fez o pedido.</p>
            )}
          </div>
          <div className={estilos.campo}>
            <label htmlFor={`${id}-nota`}>Nota interna (opcional)</label>
            <textarea
              id={`${id}-nota`}
              value={observacao}
              maxLength={TAMANHO_MAXIMO_DA_NOTA}
              onChange={(evento) => definirObservacao(evento.target.value)}
              aria-describedby={`${id}-dica-nota`}
            />
            <p id={`${id}-dica-nota`} className={estilos.dicaDoCampo}>
              <span>Só a gestão e o órgão veem. Até 280 caracteres.</span>
            </p>
          </div>
          <div className={estilos.campo}>
            <label htmlFor={`${id}-protocolo`}>Protocolo no sistema do órgão (opcional)</label>
            <input
              id={`${id}-protocolo`}
              value={protocoloDoOrgao}
              maxLength={TAMANHO_MAXIMO_DO_PROTOCOLO}
              onChange={(evento) => definirProtocolo(evento.target.value)}
            />
          </div>
          <JuntarAoMesmoProblema juntaveis={juntaveis} escolhidas={tambem} aoAlternar={alternar} />
          <QuemFicaSabendo pessoas={item.pessoasQueAcompanham} juntas={tambem.size} />
        </>
      )}

      {falha !== null && (
        <Aviso tipo="erro" titulo="A resposta não foi gravada">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
      <div className={estilos.acoes}>
        <Botao type="submit" disabled={enviando}>
          {enviando
            ? 'Enviando...'
            : tambem.size > 0 && situacao
              ? `Enviar para ${formatarNumero(tambem.size + 1)} ocorrências`
              : 'Enviar resposta'}
        </Botao>
      </div>
    </form>
  )
}
