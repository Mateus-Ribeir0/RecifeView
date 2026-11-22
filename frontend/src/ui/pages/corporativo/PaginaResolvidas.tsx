import { Link } from 'react-router'

import { useFilaDoOrgao, usePainelDoOrgao } from '../../../application/corporativo/useOrgao'
import type { OcorrenciaNaFila, PainelDoOrgao } from '../../../domain/corporativo'
import {
  formatarData,
  formatarDiaEMes,
  formatarDias,
  formatarNumero,
  formatarPorcentagem,
} from '../../../domain/formatacao'
import { nomeDaCategoria } from '../../../domain/nomes'
import { BarrasHorizontais } from '../../charts/BarrasHorizontais'
import { BarrasVerticais } from '../../charts/BarrasVerticais'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { Cartao } from '../../components/Cartao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { Medidor } from '../../components/Medidor'
import { Colunas } from '../../components/Secao'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Corporativo.module.css'
import { useNomeDoBairro } from './useNomeDoBairro'

const FONTE =
  'Fonte: encaminhamentos registrados no RecifeView. No prazo: resolvida até 30 dias depois do envio (Lei 13.460/2017, art. 16).'
const PEDIDO_DAS_RESOLVIDAS = {
  aba: 'resolvidas',
  bairro: null,
  categoria: null,
  deslocamento: 0,
} as const

function Indicadores({ painel }: { painel: PainelDoOrgao }) {
  const { indicadores } = painel
  return (
    <GradeDeKpis>
      <KpiCard
        rotulo="Resolvidas"
        valor={formatarNumero(indicadores.resolvidas)}
        contexto={`${formatarNumero(indicadores.resolvidasEm30Dias)} nos últimos 30 dias`}
      />
      <KpiCard
        rotulo="Resolvidas no prazo"
        valor={formatarPorcentagem(indicadores.pctNoPrazo)}
        contexto={`${formatarNumero(indicadores.resolvidasNoPrazo)} de ${formatarNumero(indicadores.resolvidas)} resolvidas`}
        visual={
          indicadores.pctNoPrazo === null ? undefined : (
            <Medidor porcentagem={indicadores.pctNoPrazo} rotulo="Resolvidas no prazo" />
          )
        }
      />
      <KpiCard
        rotulo="Do envio à resolução"
        valor={formatarDias(indicadores.medianaDeDiasAteResolver)}
        contexto="mediana entre o envio e a resolução"
      />
      <KpiCard
        rotulo="Pessoas com retorno"
        valor={formatarNumero(painel.pessoasComRetorno)}
        contexto="contas que acompanhavam um pedido resolvido e receberam a resposta"
      />
    </GradeDeKpis>
  )
}

function PorTema({ painel }: { painel: PainelDoOrgao }) {
  const maximo = Math.max(1, ...painel.resolvidasPorTema.map((item) => item.quantidade))
  return (
    <BarrasHorizontais
      dados={painel.resolvidasPorTema.map((item) => ({
        chave: item.rotulo,
        rotulo: nomeDaCategoria(item.rotulo),
        valor: item.quantidade,
        texto: formatarNumero(item.quantidade),
      }))}
      maximo={maximo}
      rotuloDoValor="resolvidas"
    />
  )
}

function PorSemana({ painel }: { painel: PainelDoOrgao }) {
  return (
    <BarrasVerticais
      dados={painel.semanas.map((semana) => ({
        rotulo: formatarDiaEMes(semana.inicio),
        valor: semana.resolvidas,
        texto: formatarNumero(semana.resolvidas),
      }))}
      rotuloDoEixo="Resolvidas na semana"
      altura={220}
    />
  )
}

function Resolvida({ item }: { item: OcorrenciaNaFila }) {
  const nomeDoBairro = useNomeDoBairro()
  return (
    <li className={estilos.cartao}>
      <div className={estilos.topoDoCartao}>
        <Link to={`/corporativo/ocorrencias/${item.id}`} className={estilos.codigo}>
          {item.codigo}
        </Link>
        <span className={estilos.nota}>
          {nomeDaCategoria(item.categoria)} em {nomeDoBairro(item.bairroOficial)}, pedido em{' '}
          {formatarData(item.dataAbertura)}
        </span>
      </div>
      {item.respostaAoCidadao ? (
        <blockquote className={estilos.resposta}>
          <cite>O que o órgão respondeu a quem pediu</cite>
          {item.respostaAoCidadao}
        </blockquote>
      ) : (
        <p className={estilos.nota}>Resolvida sem resposta escrita ao cidadão.</p>
      )}
    </li>
  )
}

function UltimasResolvidas() {
  const fila = useFilaDoOrgao(PEDIDO_DAS_RESOLVIDAS)
  return (
    <EstadoDaConsulta
      consulta={consultaDoCarregamento(fila)}
      estaVazia={(dados) => dados.itens.length === 0}
      mensagemDeVazio="O órgão ainda não resolveu nenhuma ocorrência pelo RecifeView."
    >
      {(dados) => (
        <ul className={estilos.lista}>
          {dados.itens.map((item) => (
            <Resolvida key={item.id} item={item} />
          ))}
        </ul>
      )}
    </EstadoDaConsulta>
  )
}

export function PaginaResolvidas() {
  useTituloDaPagina('Resolvidas')
  const painel = usePainelDoOrgao()
  return (
    <EstadoDaConsulta consulta={consultaDoCarregamento(painel)}>
      {(dados) => (
        <div className={estilos.pagina}>
          <CabecalhoDaTela titulo={`O que ${dados.nomeDoOrgao} já resolveu`} notas={[FONTE]}>
            Cada ocorrência resolvida virou uma resposta para quem pediu, no sino e por e-mail.
          </CabecalhoDaTela>
          <Indicadores painel={dados} />
          <Colunas>
            <Cartao titulo="Resolvidas por tema" nota={`${FONTE} Os 8 temas com mais resoluções.`}>
              {dados.resolvidasPorTema.length === 0 ? (
                <p>Ainda sem resolução registrada.</p>
              ) : (
                <PorTema painel={dados} />
              )}
            </Cartao>
            <Cartao titulo="Resolvidas por semana" nota={`${FONTE} Últimas 12 semanas.`}>
              <PorSemana painel={dados} />
            </Cartao>
          </Colunas>
          <Cartao titulo="As mais recentes" nota="Da resolução mais recente para a mais antiga.">
            <UltimasResolvidas />
          </Cartao>
        </div>
      )}
    </EstadoDaConsulta>
  )
}
