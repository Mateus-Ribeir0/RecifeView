import { formatarNumero } from './formatacao'

export type SituacaoPublica = 'recebido' | 'em_analise' | 'no_painel' | 'coberto_por_pedido_oficial'

export interface OcorrenciaDaCidade {
  id: string
  dataRelato: string
  servico: string
  tema: string
  bairroOficial: string
  bairro: string
  rpa: string
  via: string | null
  faixaDeNumeracao: string | null
  relatos: number
  semRetorno: number
  situacao: SituacaoPublica
}

export interface FiltroDaCidade {
  bairro: string
  tema: string
}

export interface Comparacao {
  bairro: number | null
  recife: number | null
}

export interface IndicadoresDoBairro {
  bairroOficial: string
  nome: string
  rpa: string
  populacao: number
  anoInicio: number
  anoFim: number
  pedidosAo156: number
  pedidosPorMilHabitantes: Comparacao
  prazoMediano: Comparacao
  prazoP90: Comparacao
  pctLocalRepetido: Comparacao
}

export interface ResumoDaCidade {
  relatos: number
  ocorrencias: number
  semRetorno: number
  noPainel: number
}

export const DIAS_DA_VISAO = 90
const MILISSEGUNDOS_POR_DIA = 86_400_000

export const ROTULOS_DAS_SITUACOES: Readonly<Record<SituacaoPublica, string>> = {
  recebido: 'Recebido',
  em_analise: 'Em análise pela gestão',
  no_painel: 'No painel da gestão',
  coberto_por_pedido_oficial: 'Já tem pedido oficial',
}

export const EXPLICACOES_DAS_SITUACOES: Readonly<Record<SituacaoPublica, string>> = {
  recebido: 'O relato chegou e espera a revisão da gestão.',
  em_analise: 'A gestão está conferindo se é o mesmo problema de outro relato ou pedido.',
  no_painel: 'Revisado e contado nos indicadores que a gestão acompanha.',
  coberto_por_pedido_oficial: 'Já existe um pedido na Central 156 para o mesmo lugar e serviço.',
}

export function resumirOcorrencias(lista: readonly OcorrenciaDaCidade[]): ResumoDaCidade {
  return lista.reduce<ResumoDaCidade>(
    (resumo, item) => ({
      relatos: resumo.relatos + item.relatos,
      ocorrencias: resumo.ocorrencias + 1,
      semRetorno: resumo.semRetorno + item.semRetorno,
      noPainel: resumo.noPainel + (item.situacao === 'no_painel' ? 1 : 0),
    }),
    { relatos: 0, ocorrencias: 0, semRetorno: 0, noPainel: 0 },
  )
}

export function descreverLocal(ocorrencia: OcorrenciaDaCidade): string {
  if (!ocorrencia.via) return `${ocorrencia.bairro}, rua não identificada`
  const faixa = ocorrencia.faixaDeNumeracao ? `, ${ocorrencia.faixaDeNumeracao}` : ''
  return `${ocorrencia.via}${faixa}`
}

export function haQuantoTempo(dataIso: string, hoje: Date): string {
  const dia = new Date(`${dataIso}T12:00:00`)
  const dias = Math.max(0, Math.round((hoje.getTime() - dia.getTime()) / MILISSEGUNDOS_POR_DIA))
  if (dias === 0) return 'hoje'
  if (dias === 1) return 'ontem'
  return `há ${formatarNumero(dias)} dias`
}

export function bairrosComRelato(lista: readonly OcorrenciaDaCidade[]): ReadonlySet<string> {
  return new Set(lista.map((item) => item.bairroOficial))
}
