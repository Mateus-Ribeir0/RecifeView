import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'

import { useServicoDeEncaminhamentos } from '../../../application/encaminhamentos/contexto'
import { useEncaminhamento } from '../../../application/encaminhamentos/useEncaminhamentos'
import {
  podeEncaminharDeNovo,
  podeReenviar,
  respostasPossiveis,
  ROTULOS_DOS_CANAIS,
  type Encaminhamento,
  type RespostaAoEncaminhamento,
} from '../../../domain/encaminhamentos'
import { formatarData, formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { Cartao } from '../../components/Cartao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { Colunas } from '../../components/Secao'
import estilos from './Encaminhamentos.module.css'
import { FormularioDeRetorno } from './FormularioDeRetorno'
import { LinhaDoTempo } from './LinhaDoTempo'
import { PainelDeEncaminhamento } from './PainelDeEncaminhamento'
import { SeloDoEncaminhamento } from './SeloDoEncaminhamento'

function DadosDoEnvio({ item }: { item: Encaminhamento }) {
  const sugeridoOutro = item.orgaoSugerido && item.orgaoSugerido !== item.orgao
  return (
    <dl className={estilos.resumoDaOcorrencia}>
      <div>
        <dt>Situação</dt>
        <dd>
          <SeloDoEncaminhamento situacao={item.situacao} atrasado={item.atrasado} />
        </dd>
      </div>
      <div>
        <dt>Prazo para resolver ou devolver</dt>
        <dd>{formatarData(item.prazoDeResposta)}</dd>
      </div>
      <div>
        <dt>Como saiu</dt>
        <dd>
          {item.automatico ? 'Envio automático' : 'Pela gestão'}, {ROTULOS_DOS_CANAIS[item.canal]}
        </dd>
      </div>
      <div>
        <dt>Protocolo no órgão</dt>
        <dd>{item.protocoloDoOrgao ?? 'ainda não informado'}</dd>
      </div>
      {item.lembreteEnviadoEm && (
        <div>
          <dt>Lembrete ao órgão</dt>
          <dd>enviado em {formatarDataEHora(item.lembreteEnviadoEm)}</dd>
        </div>
      )}
      <div>
        <dt>Nota na fila</dt>
        <dd>{item.nota === null ? 'não informada' : `${formatarNumero(item.nota, 1)} de 10`}</dd>
      </div>
      {sugeridoOutro && (
        <div>
          <dt>Sugestão do sistema</dt>
          <dd>{item.nomeDoOrgaoSugerido}, trocada pela gestão</dd>
        </div>
      )}
    </dl>
  )
}

function DadosDaOcorrencia({ item }: { item: Encaminhamento }) {
  const { ocorrencia } = item
  return (
    <dl className={estilos.resumoDaOcorrencia}>
      <div>
        <dt>Fonte</dt>
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
        <dt>Tema</dt>
        <dd>{nomeDaCategoria(ocorrencia.categoria)}</dd>
      </div>
      <div>
        <dt>Serviço</dt>
        <dd>{nomeDaCategoria(ocorrencia.servico)}</dd>
      </div>
      <div>
        <dt>Situação na fonte</dt>
        <dd>{nomeDaCategoria(ocorrencia.situacao)}</dd>
      </div>
      {ocorrencia.referenciaDeLocal && (
        <div>
          <dt>Local aproximado (foi na mensagem)</dt>
          <dd>{ocorrencia.referenciaDeLocal}</dd>
        </div>
      )}
    </dl>
  )
}

function OutroDestino({ item }: { item: Encaminhamento }) {
  const navegar = useNavigate()
  const [escolhendo, definirEscolhendo] = useState(false)
  if (escolhendo) {
    return (
      <PainelDeEncaminhamento
        chaveRegistro={item.ocorrencia.chaveRegistro}
        nota={item.nota}
        contribuicaoId={item.contribuicaoId}
        aoFechar={() => definirEscolhendo(false)}
        aoConcluir={(novo) => void navegar(`/painel/encaminhamentos/${novo.id}`)}
      />
    )
  }
  return (
    <Cartao titulo="O órgão devolveu a ocorrência">
      <p>
        {item.nomeDoOrgao} informou que a ocorrência não é com ele. Escolha outro órgão: quem
        acompanha o pedido é avisado do novo destino.
      </p>
      <div className={estilos.acoes}>
        <Botao onClick={() => definirEscolhendo(true)}>Encaminhar para outro órgão</Botao>
      </div>
    </Cartao>
  )
}

interface AcoesProps {
  item: Encaminhamento
  aoAtualizar: () => void
}

function AcoesDoEncaminhamento({ item, aoAtualizar }: AcoesProps) {
  const servico = useServicoDeEncaminhamentos()
  const [falha, definirFalha] = useState<unknown>(null)
  const respostas = respostasPossiveis(item.situacao)

  async function responder(resposta: RespostaAoEncaminhamento) {
    await servico.registrarRetorno(item.id, resposta)
    aoAtualizar()
  }

  async function reenviar() {
    definirFalha(null)
    try {
      await servico.reenviar(item.id)
      aoAtualizar()
    } catch (motivo) {
      definirFalha(motivo)
    }
  }

  if (podeReenviar(item)) {
    return (
      <Cartao titulo="O canal do órgão não aceitou a mensagem">
        <p>
          Confira o canal configurado para {item.nomeDoOrgao} e reenvie. Um link novo substitui o
          anterior.
        </p>
        {falha !== null && (
          <Aviso tipo="erro">
            <p>{mensagemDeFalha(falha)}</p>
          </Aviso>
        )}
        <div className={estilos.acoes}>
          <Botao onClick={() => void reenviar()}>Reenviar</Botao>
        </div>
      </Cartao>
    )
  }
  if (podeEncaminharDeNovo(item.situacao)) {
    return <OutroDestino item={item} />
  }
  if (respostas.length === 0) {
    return (
      <Cartao titulo="Ciclo encerrado">
        <p>
          O órgão informou que resolveu. Quem fez o pedido e tem conta recebeu o aviso por e-mail;
          quem não tem acompanha pelo protocolo.
        </p>
      </Cartao>
    )
  }
  return (
    <Cartao titulo="O órgão respondeu por outro meio?">
      <p className={estilos.nota}>
        Registre aqui o que veio por telefone, ofício ou e-mail. O órgão também pode responder pelo
        link da mensagem.
      </p>
      <FormularioDeRetorno
        respostas={respostas}
        rotuloDoBotao="Registrar o retorno"
        aoResponder={responder}
      />
    </Cartao>
  )
}

export function PaginaDoEncaminhamento() {
  const { id } = useParams()
  const encaminhamento = useEncaminhamento(Number(id))

  return (
    <EstadoDaConsulta consulta={consultaDoCarregamento(encaminhamento)}>
      {(item) => (
        <div className={estilos.detalhe}>
          <CabecalhoDaTela
            titulo={item.codigo}
            acoes={
              <Link to="/painel/encaminhamentos" className={estilos.nota}>
                Voltar para Encaminhamentos
              </Link>
            }
          >
            Ocorrência de {nomeDaFonte(item.ocorrencia.fonte)} encaminhada para {item.nomeDoOrgao}{' '}
            em {formatarDataEHora(item.criadoEm)}.
          </CabecalhoDaTela>
          <Colunas proporcao="larga">
            <div className={estilos.detalhe}>
              <Cartao titulo="O envio">
                <DadosDoEnvio item={item} />
                {item.justificativa && <p>Justificativa da gestão: {item.justificativa}</p>}
              </Cartao>
              <Cartao titulo="A ocorrência">
                <DadosDaOcorrencia item={item} />
              </Cartao>
              <AcoesDoEncaminhamento item={item} aoAtualizar={encaminhamento.recarregar} />
            </div>
            <Cartao titulo="Etapas">
              <LinhaDoTempo eventos={item.eventos} comObservacao />
            </Cartao>
          </Colunas>
        </div>
      )}
    </EstadoDaConsulta>
  )
}
