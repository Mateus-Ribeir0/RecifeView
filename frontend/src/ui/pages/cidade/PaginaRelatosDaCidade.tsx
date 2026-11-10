import { Suspense, useId, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useOcorrenciasDaCidade } from '../../../application/cidade/useCidade'
import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import {
  bairrosComRelato,
  DIAS_DA_VISAO,
  ROTULOS_DAS_SITUACOES,
  EXPLICACOES_DAS_SITUACOES,
  resumirOcorrencias,
  type SituacaoPublica,
} from '../../../domain/cidade'
import { formatarNumero } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import campo from '../../components/Campo.module.css'
import { Icone, type NomeDoIcone } from '../../components/Icone'
import { KpiCard } from '../../components/KpiCard'
import { LinkDeBotao } from '../../components/LinkDeBotao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { MapaDeEscolhaDoBairro } from '../../map/MapaDeEscolhaDoBairro'
import { CartaoDeOcorrencia, SeloDaSituacao } from './CartaoDeOcorrencia'
import estilos from './Cidade.module.css'

const ICONES_DOS_TEMAS: Readonly<Record<string, NomeDoIcone>> = {
  iluminacao: 'lampada',
  limpeza: 'limpeza',
  arvores: 'arvore',
  drenagem: 'gota',
  ruas: 'via',
}
const SITUACOES = Object.keys(ROTULOS_DAS_SITUACOES) as SituacaoPublica[]

function Legenda() {
  return (
    <dl className={estilos.legendaDasSituacoes}>
      {SITUACOES.map((situacao) => (
        <div key={situacao}>
          <dt>
            <SeloDaSituacao situacao={situacao} />
          </dt>
          <dd>{EXPLICACOES_DAS_SITUACOES[situacao]}</dd>
        </div>
      ))}
    </dl>
  )
}

export function PaginaRelatosDaCidade() {
  useTituloDaPagina('Relatos da cidade')
  const { estado } = useSessao()
  const [parametros, definirParametros] = useSearchParams()
  const meuBairro = estado.situacao === 'autenticada' ? (estado.usuario.bairroOficial ?? '') : ''
  const bairro = parametros.get('bairro') ?? meuBairro
  const [tema, definirTema] = useState('')
  const idDoBairro = useId()
  const { catalogo } = useCatalogoDoFormulario()
  const { dados, erro, carregando } = useOcorrenciasDaCidade({ bairro, tema })
  const { dados: daCidade } = useOcorrenciasDaCidade({ bairro: '', tema })
  const hoje = useMemo(() => new Date(), [])
  const lista = dados ?? []
  const resumo = resumirOcorrencias(lista)
  const nomeDoBairro = catalogo?.bairros.find((item) => item.chave === bairro)?.nome

  function escolherBairro(chave: string) {
    definirParametros(chave ? { bairro: chave } : { bairro: '' }, { replace: true })
  }

  return (
    <>
      <div className={estilos.cabecalhoDaPagina}>
        <div>
          <h1 className={estilos.titulo}>Relatos da cidade</h1>
          <p className={estilos.subtitulo}>
            O que as pessoas relataram nos últimos {DIAS_DA_VISAO} dias
            {nomeDoBairro ? ` em ${nomeDoBairro}` : ' no Recife'} e em que pé está cada caso.
          </p>
        </div>
        <LinkDeBotao para="/cidade/relatar" compacto>
          Relatar um problema
        </LinkDeBotao>
      </div>
      <div className={estilos.filtros}>
        <div className={campo.campo}>
          <label htmlFor={idDoBairro} className={campo.rotulo}>
            Bairro
          </label>
          <select
            id={idDoBairro}
            className={campo.entrada}
            value={bairro}
            onChange={(evento) => escolherBairro(evento.target.value)}
          >
            <option value="">Recife inteiro</option>
            {catalogo?.bairros.map(({ chave, nome }) => (
              <option key={chave} value={chave}>
                {nome}
              </option>
            ))}
          </select>
        </div>
        <div className={estilos.temas} role="group" aria-label="Tema">
          <button type="button" aria-pressed={tema === ''} onClick={() => definirTema('')}>
            Todos
          </button>
          {catalogo?.temas.map(({ chave, rotulo }) => (
            <button
              key={chave}
              type="button"
              aria-pressed={tema === chave}
              onClick={() => definirTema(chave)}
            >
              <Icone nome={ICONES_DOS_TEMAS[chave] ?? 'relato'} tamanho={16} />
              {rotulo}
            </button>
          ))}
        </div>
      </div>
      <div className={estilos.kpis}>
        <KpiCard
          rotulo="Relatos"
          valor={formatarNumero(resumo.relatos)}
          contexto="pessoas que relataram"
        />
        <KpiCard
          rotulo="Ocorrências"
          valor={formatarNumero(resumo.ocorrencias)}
          contexto="relatos iguais contam uma vez"
        />
        <KpiCard
          rotulo="Sem retorno"
          valor={formatarNumero(resumo.semRetorno)}
          contexto="já tinham pedido antes e não tiveram resposta"
        />
        <KpiCard
          rotulo="No painel da gestão"
          valor={formatarNumero(resumo.noPainel)}
          contexto="revisadas e contadas nos indicadores"
        />
      </div>
      <div className={estilos.grade}>
        <figure className={estilos.mapa}>
          <Suspense fallback={<div className={estilos.reservaDoMapa} />}>
            <MapaDeEscolhaDoBairro
              marcados={bairrosComRelato(daCidade ?? [])}
              escolhido={bairro}
              aoEscolher={escolherBairro}
            />
          </Suspense>
          <figcaption>
            <span className={estilos.amostraComRelato} aria-hidden="true" /> Bairro com relato nos
            últimos {DIAS_DA_VISAO} dias. Clique num bairro para filtrar.
          </figcaption>
        </figure>
        <section aria-label="Lista de relatos" className={estilos.lista}>
          {erro ? (
            <Aviso tipo="erro" titulo="Não foi possível carregar os relatos">
              {mensagemDeFalha(erro)}
            </Aviso>
          ) : null}
          {carregando && !dados ? <div className={estilos.esqueleto} aria-busy="true" /> : null}
          {!carregando && !erro && lista.length === 0 && (
            <div className={estilos.vazio}>
              <p>
                Nenhum relato {nomeDoBairro ? `em ${nomeDoBairro}` : 'com estes filtros'} nos
                últimos {DIAS_DA_VISAO} dias.
              </p>
              <LinkDeBotao para="/cidade/relatar" variante="secundario" compacto>
                Relatar o primeiro
              </LinkDeBotao>
            </div>
          )}
          {lista.map((ocorrencia) => (
            <CartaoDeOcorrencia key={ocorrencia.id} ocorrencia={ocorrencia} hoje={hoje} />
          ))}
        </section>
      </div>
      <details className={estilos.comoLer}>
        <summary>O que cada situação quer dizer</summary>
        <Legenda />
      </details>
      <p className={estilos.nota}>
        Fonte: relatos do formulário do RecifeView, últimos {DIAS_DA_VISAO} dias, n ={' '}
        {formatarNumero(resumo.ocorrencias)} ocorrências. A rua aparece só quando está na lista
        oficial de vias do 156, e o número aparece como faixa de 100, para proteger quem relatou.
        Ninguém vê o texto escrito nem quem enviou.
      </p>
    </>
  )
}
