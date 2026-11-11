import { useState } from 'react'
import { useParams } from 'react-router'

import { useServicoDeRetornoDoOrgao } from '../../../application/encaminhamentos/contexto'
import { useEncaminhamentoPeloLink } from '../../../application/encaminhamentos/useEncaminhamentos'
import type {
  EncaminhamentoParaOOrgao,
  RespostaAoEncaminhamento,
} from '../../../domain/encaminhamentos'
import { formatarData } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Aviso } from '../../components/Aviso'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from '../encaminhamentos/Encaminhamentos.module.css'
import { FormularioDeRetorno } from '../encaminhamentos/FormularioDeRetorno'
import { LinhaDoTempo } from '../encaminhamentos/LinhaDoTempo'
import { SeloDoEncaminhamento } from '../encaminhamentos/SeloDoEncaminhamento'

function OQueChegou({ item }: { item: EncaminhamentoParaOOrgao }) {
  const { ocorrencia } = item
  return (
    <dl className={estilos.resumoDaOcorrencia}>
      <div>
        <dt>Situação</dt>
        <dd>
          <SeloDoEncaminhamento situacao={item.situacao} />
        </dd>
      </div>
      <div>
        <dt>Prazo para resolver ou devolver</dt>
        <dd>{formatarData(item.prazoDeResposta)}</dd>
      </div>
      <div>
        <dt>Canal de origem</dt>
        <dd>{nomeDaFonte(ocorrencia.fonte)}</dd>
      </div>
      <div>
        <dt>Protocolo de origem</dt>
        <dd>{ocorrencia.protocolo ?? 'a fonte não publica'}</dd>
      </div>
      <div>
        <dt>Aberta em</dt>
        <dd>{formatarData(ocorrencia.dataAbertura)}</dd>
      </div>
      <div>
        <dt>Tema e serviço</dt>
        <dd>
          {nomeDaCategoria(ocorrencia.categoria)}
          {ocorrencia.servico ? `: ${nomeDaCategoria(ocorrencia.servico)}` : ''}
        </dd>
      </div>
      <div>
        <dt>Bairro</dt>
        <dd>
          {nomeDaCategoria(ocorrencia.bairroOficial)}
          {ocorrencia.rpa ? ` (RPA ${ocorrencia.rpa})` : ''}
        </dd>
      </div>
    </dl>
  )
}

function Retorno({ token, item }: { token: string; item: EncaminhamentoParaOOrgao }) {
  const servico = useServicoDeRetornoDoOrgao()
  const [atual, definirAtual] = useState(item)

  async function responder(resposta: RespostaAoEncaminhamento) {
    definirAtual(await servico.responder(token, resposta))
  }

  return (
    <div className={estilos.detalhe}>
      <header>
        <h1>{atual.codigo}</h1>
        <p>
          Ocorrência encaminhada para {atual.nomeDoOrgao} em {formatarData(atual.criadoEm)}.
        </p>
      </header>
      <OQueChegou item={atual} />
      {atual.justificativa && <p>Por que a gestão encaminhou: {atual.justificativa}</p>}
      {atual.respostasPossiveis.length > 0 ? (
        <FormularioDeRetorno
          respostas={atual.respostasPossiveis}
          rotuloDoBotao="Enviar a resposta"
          aoResponder={responder}
        />
      ) : (
        <Aviso tipo="sucesso" titulo="Resposta registrada">
          <p>
            Este encaminhamento está encerrado. A gestão e quem fez o pedido já veem a resposta.
          </p>
        </Aviso>
      )}
      <section aria-label="Etapas">
        <h2 className={estilos.nota}>Etapas</h2>
        <LinhaDoTempo eventos={atual.eventos} />
      </section>
    </div>
  )
}

export function PaginaRetornoDoOrgao() {
  useTituloDaPagina('Retorno do órgão')
  const { token = '' } = useParams()
  const encaminhamento = useEncaminhamentoPeloLink(token)

  return (
    <LayoutDeAcesso tom="orgao">
      <EstadoDaConsulta consulta={consultaDoCarregamento(encaminhamento)}>
        {(item) => <Retorno token={token} item={item} />}
      </EstadoDaConsulta>
    </LayoutDeAcesso>
  )
}
