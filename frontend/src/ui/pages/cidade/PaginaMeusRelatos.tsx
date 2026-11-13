import { useMemo } from 'react'

import { useMeusRelatos } from '../../../application/cidade/useCidade'
import {
  contarPorSituacao,
  etapasDoRelato,
  EXPLICACOES_DAS_SITUACOES,
  haQuantoTempo,
  ROTULOS_DAS_SITUACOES,
  type MeuRelato,
  type SituacaoPublica,
} from '../../../domain/cidade'
import { contar, formatarNumero } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { Icone } from '../../components/Icone'
import { KpiCard } from '../../components/KpiCard'
import { LinkDeBotao } from '../../components/LinkDeBotao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { EtapasDoEncaminhamento } from '../pedidos/CartaoDoAndamento'
import { IconeDoTema, SeloDaSituacao } from './CartaoDeOcorrencia'
import estilos from './Cidade.module.css'
import meus from './MeusRelatos.module.css'

const DIAS_DE_GUARDA_DO_ENDERECO = 90
const SITUACOES = Object.keys(ROTULOS_DAS_SITUACOES) as SituacaoPublica[]

function Etapas({ relato }: { relato: MeuRelato }) {
  return (
    <ol className={meus.etapas} aria-label="Andamento do relato">
      {etapasDoRelato(relato.situacao).map(({ situacao, estado }) => (
        <li
          key={situacao}
          data-estado={estado}
          aria-current={estado === 'atual' ? 'step' : undefined}
        >
          <span className={meus.marca} aria-hidden="true">
            {estado === 'feita' ? <Icone nome="confirmado" tamanho={14} /> : null}
          </span>
          {ROTULOS_DAS_SITUACOES[situacao]}
        </li>
      ))}
    </ol>
  )
}

function Endereco({ relato }: { relato: MeuRelato }) {
  if (relato.endereco) return <p className={estilos.local}>{relato.endereco}</p>
  const motivo = relato.enderecoApagado
    ? `Endereço apagado depois de ${DIAS_DE_GUARDA_DO_ENDERECO} dias, para proteger a sua privacidade`
    : 'Sem endereço informado'
  return <p className={meus.semEndereco}>{motivo}</p>
}

function CartaoDoMeuRelato({ relato, hoje }: { relato: MeuRelato; hoje: Date }) {
  const outras = relato.relatos - 1
  return (
    <article className={estilos.cartao}>
      <IconeDoTema tema={relato.tema} />
      <div className={estilos.corpoDoCartao}>
        <div className={estilos.topoDoCartao}>
          <h3>{relato.servico}</h3>
          <SeloDaSituacao situacao={relato.situacao} />
        </div>
        <Endereco relato={relato} />
        {relato.detalhe ? <p className={meus.oQueEscreveu}>“{relato.detalhe}”</p> : null}
        <p className={estilos.detalhe}>
          {relato.bairro} · enviado {haQuantoTempo(relato.recebidoEm.slice(0, 10), hoje)}
        </p>
        {outras > 0 || relato.somado ? (
          <ul className={estilos.contagens}>
            {outras > 0 && (
              <li>
                <Icone nome="pessoas" tamanho={16} />
                {contar(outras, 'outra pessoa relatou o mesmo', 'outras pessoas relataram o mesmo')}
              </li>
            )}
            {relato.somado && (
              <li>
                <Icone nome="somar" tamanho={16} />
                Somado a um relato que já existia
              </li>
            )}
          </ul>
        ) : null}
        <Etapas relato={relato} />
        <p className={meus.explicacao}>{EXPLICACOES_DAS_SITUACOES[relato.situacao]}</p>
        {relato.encaminhamento && <EtapasDoEncaminhamento item={relato.encaminhamento} />}
      </div>
    </article>
  )
}

function ComoORelatoAnda() {
  return (
    <aside className={meus.lateral} aria-labelledby="titulo-como-anda">
      <h2 id="titulo-como-anda">Como o relato anda</h2>
      <dl>
        {SITUACOES.map((situacao) => (
          <div key={situacao}>
            <dt>
              <SeloDaSituacao situacao={situacao} />
            </dt>
            <dd>{EXPLICACOES_DAS_SITUACOES[situacao]}</dd>
          </div>
        ))}
      </dl>
      <p>O relato não gera protocolo de atendimento. Para pedir o serviço, use a Central 156.</p>
    </aside>
  )
}

function Vazio() {
  return (
    <div className={estilos.vazio}>
      <p>
        Você ainda não relatou nada com a conta aberta. Relatos enviados sem entrar não aparecem
        aqui, porque não ficam ligados a ninguém.
      </p>
      <LinkDeBotao para="/cidade/relatar" variante="secundario" compacto>
        Relatar um problema
      </LinkDeBotao>
    </div>
  )
}

export function PaginaMeusRelatos() {
  useTituloDaPagina('Meus relatos')
  const { dados, erro, carregando } = useMeusRelatos()
  const hoje = useMemo(() => new Date(), [])
  const lista = dados ?? []
  const contagem = contarPorSituacao(lista)

  return (
    <>
      <div className={estilos.cabecalhoDaPagina}>
        <div>
          <h1 className={estilos.titulo}>Meus relatos</h1>
          <p className={estilos.subtitulo}>
            Os problemas que você relatou com a conta aberta e em que pé está cada um.
          </p>
        </div>
        <LinkDeBotao para="/cidade/relatar" compacto>
          Relatar um problema
        </LinkDeBotao>
      </div>
      <div className={meus.kpis}>
        <KpiCard
          rotulo="Relatos enviados"
          valor={formatarNumero(lista.length)}
          contexto="com a sua conta aberta"
        />
        <KpiCard
          rotulo="Esperando a gestão"
          valor={formatarNumero(contagem.recebido + contagem.em_analise)}
          contexto="recebidos ou em conferência"
        />
        <KpiCard
          rotulo="Já revisados"
          valor={formatarNumero(contagem.no_painel + contagem.coberto_por_pedido_oficial)}
          contexto="no painel da gestão ou com pedido oficial"
        />
      </div>
      <div className={meus.grade}>
        <section aria-label="Meus relatos" className={meus.lista}>
          {erro ? (
            <Aviso tipo="erro" titulo="Não foi possível carregar os seus relatos">
              {mensagemDeFalha(erro)}
            </Aviso>
          ) : null}
          {carregando && !dados ? <div className={estilos.esqueleto} aria-busy="true" /> : null}
          {!carregando && !erro && lista.length === 0 && <Vazio />}
          {lista.map((relato) => (
            <CartaoDoMeuRelato key={relato.id} relato={relato} hoje={hoje} />
          ))}
        </section>
        <ComoORelatoAnda />
      </div>
      <p className={estilos.nota}>
        Fonte: relatos que você enviou pelo RecifeView com a conta aberta, n ={' '}
        {formatarNumero(lista.length)}. Só você vê esta lista: a gestão revisa os relatos sem saber
        quem enviou. O endereço e o texto ficam guardados por {DIAS_DE_GUARDA_DO_ENDERECO} dias e
        depois são apagados.
      </p>
    </>
  )
}
