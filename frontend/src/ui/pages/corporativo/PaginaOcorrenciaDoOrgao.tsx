import { Suspense, useState } from 'react'
import { Link, useParams } from 'react-router'

import { useOcorrenciaDoOrgao } from '../../../application/corporativo/useOrgao'
import {
  ETAPAS_NO_ORGAO,
  type EventoDoOrgao,
  type OcorrenciaDoOrgao,
  type RespostaRegistrada,
} from '../../../domain/corporativo'
import { ROTULOS_DOS_AUTORES } from '../../../domain/encaminhamentos'
import { contar, formatarData, formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Aviso } from '../../components/Aviso'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { Cartao } from '../../components/Cartao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { Colunas } from '../../components/Secao'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { MapaDeEscolhaDoBairro } from '../../map/MapaDeEscolhaDoBairro'
import { SeloDoEncaminhamento } from '../encaminhamentos/SeloDoEncaminhamento'
import estilos from './Corporativo.module.css'
import { FormularioDeResposta } from './FormularioDeResposta'
import { ListaDoMesmoProblema } from './ListaDoMesmoProblema'
import { PrazoRestante } from './PrazoRestante'
import { useNomeDoBairro } from './useNomeDoBairro'

const CAMINHO_DA_FILA = '/corporativo/ocorrencias'

function OQueFoiPedido({ item }: { item: OcorrenciaDoOrgao }) {
  return (
    <dl className={estilos.dados}>
      <div>
        <dt>Tema</dt>
        <dd>{nomeDaCategoria(item.categoria)}</dd>
      </div>
      <div>
        <dt>Serviço</dt>
        <dd>{nomeDaCategoria(item.servico)}</dd>
      </div>
      <div>
        <dt>Fonte</dt>
        <dd>{nomeDaFonte(item.fonte)}</dd>
      </div>
      <div>
        <dt>Pedido em</dt>
        <dd>{formatarData(item.dataAbertura)}</dd>
      </div>
      <div>
        <dt>Protocolo de origem</dt>
        <dd>{item.protocoloDeOrigem ?? 'a fonte não publica'}</dd>
      </div>
      <div>
        <dt>Situação na fonte</dt>
        <dd>{nomeDaCategoria(item.situacaoNaFonte)}</dd>
      </div>
      <div>
        <dt>Encaminhada em</dt>
        <dd>{formatarDataEHora(item.criadoEm)}</dd>
      </div>
      <div>
        <dt>Nota de prioridade</dt>
        <dd>{item.nota === null ? 'não informada' : `${formatarNumero(item.nota, 1)} de 10`}</dd>
      </div>
    </dl>
  )
}

function Onde({ item }: { item: OcorrenciaDoOrgao }) {
  const nomeDoBairro = useNomeDoBairro()
  const bairro = nomeDoBairro(item.bairroOficial)
  return (
    <div className={estilos.coluna}>
      <dl className={estilos.dados}>
        <div>
          <dt>Bairro</dt>
          <dd>
            {bairro}
            {item.rpa && ` (RPA ${item.rpa})`}
          </dd>
        </div>
        <div>
          <dt>Rua e faixa de numeração</dt>
          <dd>{item.localAproximado ?? 'a fonte não traz o endereço'}</dd>
        </div>
      </dl>
      {item.bairroOficial && (
        <Suspense fallback={<p className={estilos.nota}>Carregando o mapa...</p>}>
          <div className={estilos.mapaDoBairro}>
            <MapaDeEscolhaDoBairro
              marcados={new Set([item.bairroOficial])}
              escolhido={item.bairroOficial}
              aoEscolher={() => undefined}
              descricao={`Mapa do Recife com o bairro ${bairro} em destaque.`}
            />
          </div>
        </Suspense>
      )}
      <p className={estilos.nota}>
        O endereço exato não sai do RecifeView: quem relatou pode morar no lugar. A rua só aparece
        quando está na lista oficial de vias, com a numeração de 100 em 100.
      </p>
    </div>
  )
}

function Evento({ evento }: { evento: EventoDoOrgao }) {
  return (
    <li>
      <time dateTime={evento.ocorridoEm}>{formatarDataEHora(evento.ocorridoEm)}</time>
      <strong>
        {ETAPAS_NO_ORGAO[evento.situacao]}, {ROTULOS_DOS_AUTORES[evento.autor]}
      </strong>
      {evento.previsao && <span>Previsão de conclusão: {formatarData(evento.previsao)}</span>}
      {evento.respostaAoCidadao && (
        <blockquote className={estilos.resposta}>
          <cite>Resposta ao cidadão</cite>
          {evento.respostaAoCidadao}
        </blockquote>
      )}
      {evento.observacao && (
        <span className={estilos.notaInterna}>Nota interna: {evento.observacao}</span>
      )}
      {evento.protocoloDoOrgao && (
        <span className={estilos.nota}>Protocolo no órgão: {evento.protocoloDoOrgao}</span>
      )}
    </li>
  )
}

function Responder({ item, aoResponder }: DetalheProps) {
  if (!item.podeResponder) {
    return (
      <Cartao titulo="Ciclo encerrado">
        <p>
          {item.situacao === 'resolvido'
            ? 'O órgão informou que resolveu. Quem acompanha o pedido recebeu a resposta.'
            : 'O órgão devolveu a ocorrência. A gestão vai escolher outro destino.'}
        </p>
      </Cartao>
    )
  }
  return (
    <Cartao titulo="Responder">
      <FormularioDeResposta item={item} aoResponder={aoResponder} />
    </Cartao>
  )
}

function AvisoDeResposta({ registrada }: { registrada: RespostaRegistrada | null }) {
  if (!registrada) return null
  const juntas = registrada.codigosJuntos
  return (
    <Aviso tipo="sucesso" titulo="Resposta registrada">
      <p>
        {registrada.codigo} está agora como {ETAPAS_NO_ORGAO[registrada.situacao].toLowerCase()}
        {juntas.length > 0 && `, junto com ${juntas.join(', ')}`}. Quem acompanha recebeu o aviso no
        sino e por e-mail.
      </p>
    </Aviso>
  )
}

interface DetalheProps {
  item: OcorrenciaDoOrgao
  aoResponder: (registrada: RespostaRegistrada) => void
}

function Detalhe({ item, aoResponder }: DetalheProps) {
  return (
    <div className={estilos.pagina}>
      <CabecalhoDaTela
        titulo={item.codigo}
        acoes={
          <Link to={CAMINHO_DA_FILA} className={estilos.voltar}>
            Voltar para Ocorrências
          </Link>
        }
      >
        <SeloDoEncaminhamento
          situacao={item.situacao}
          atrasado={item.atrasado}
          rotulo={ETAPAS_NO_ORGAO[item.situacao]}
        />{' '}
        <PrazoRestante item={item} />
        {item.pessoasQueAcompanham > 0 &&
          `. ${contar(item.pessoasQueAcompanham, 'pessoa acompanha', 'pessoas acompanham')} este pedido`}
        .
      </CabecalhoDaTela>
      <Colunas proporcao="larga">
        <div className={estilos.coluna}>
          <Cartao titulo="O que foi pedido">
            <OQueFoiPedido item={item} />
            {item.justificativa && <p>Por que a gestão encaminhou: {item.justificativa}</p>}
          </Cartao>
          <Cartao titulo="Onde fica">
            <Onde item={item} />
          </Cartao>
          <Cartao titulo="Mesmo problema">
            <ListaDoMesmoProblema
              parecidos={item.mesmoProblema}
              registrosDoMesmoLocal={item.registrosDoMesmoLocal}
              fonte={item.fonte}
              caminhoDoDetalhe={(id) => `${CAMINHO_DA_FILA}/${id}`}
            />
          </Cartao>
        </div>
        <div className={estilos.coluna}>
          <Responder item={item} aoResponder={aoResponder} />
          <Cartao titulo="Etapas">
            <ol className={estilos.linhaDoTempo} aria-label="Etapas da ocorrência">
              {item.eventos.map((evento, indice) => (
                <Evento key={`${evento.ocorridoEm}-${indice}`} evento={evento} />
              ))}
            </ol>
          </Cartao>
        </div>
      </Colunas>
    </div>
  )
}

export function PaginaOcorrenciaDoOrgao() {
  const { id } = useParams()
  const ocorrencia = useOcorrenciaDoOrgao(Number(id))
  const [registrada, definirRegistrada] = useState<RespostaRegistrada | null>(null)
  useTituloDaPagina(ocorrencia.dados?.codigo ?? 'Ocorrência')

  function aoResponder(resposta: RespostaRegistrada) {
    definirRegistrada(resposta)
    ocorrencia.recarregar()
  }

  return (
    <div className={estilos.pagina}>
      <AvisoDeResposta registrada={registrada} />
      <EstadoDaConsulta consulta={consultaDoCarregamento(ocorrencia)}>
        {(item) => <Detalhe item={item} aoResponder={aoResponder} />}
      </EstadoDaConsulta>
    </div>
  )
}
