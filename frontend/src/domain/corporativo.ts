import type {
  AutorDoEvento,
  GrupoDoMesmoProblema,
  IndicadoresDoOrgao,
  MesmoProblema,
  Orgao,
  RespostaPossivel,
  SemanaDoCiclo,
  SituacaoDoEncaminhamento,
} from './encaminhamentos'
import { contar } from './formatacao'

export type AbaDoOrgao =
  'novas' | 'em_atendimento' | 'vencidas' | 'resolvidas' | 'devolvidas' | 'todas'

export const ABAS_DO_ORGAO: readonly AbaDoOrgao[] = [
  'novas',
  'em_atendimento',
  'vencidas',
  'resolvidas',
  'devolvidas',
  'todas',
]

export const ROTULOS_DAS_ABAS: Readonly<Record<AbaDoOrgao, string>> = {
  novas: 'A responder',
  em_atendimento: 'Em atendimento',
  vencidas: 'Prazo vencido',
  resolvidas: 'Resolvidas',
  devolvidas: 'Devolvidas',
  todas: 'Todas',
}

/** Como a etapa se chama para quem está do lado do órgão. */
export const ETAPAS_NO_ORGAO: Readonly<Record<SituacaoDoEncaminhamento, string>> = {
  enviado: 'A responder',
  recebido: 'Em atendimento',
  resolvido: 'Resolvida',
  devolvido: 'Devolvida à gestão',
  falhou: 'Falha no envio',
}

export const ACOES_DO_ORGAO: Readonly<Record<RespostaPossivel, string>> = {
  recebido: 'Em atendimento',
  resolvido: 'Resolvida',
  devolvido: 'Devolver à gestão',
}

export interface OcorrenciaNaFila {
  id: number
  codigo: string
  fonte: string
  categoria: string | null
  servico: string | null
  bairroOficial: string | null
  rpa: string | null
  localAproximado: string | null
  dataAbertura: string | null
  situacao: SituacaoDoEncaminhamento
  atrasado: boolean
  criadoEm: string
  prazoDeResposta: string
  diasParaOPrazo: number
  previsao: string | null
  respostaAoCidadao: string | null
  mesmoProblemaNoOrgao: number
  mesmoProblemaEmOutrosOrgaos: number
  pessoasQueAcompanham: number
}

export interface FilaDoOrgao {
  hoje: string
  itens: readonly OcorrenciaNaFila[]
  total: number
  porAba: Readonly<Record<AbaDoOrgao, number>>
  bairros: readonly string[]
  categorias: readonly string[]
}

export interface PedidoDaFila {
  aba: AbaDoOrgao
  bairro: string | null
  categoria: string | null
  deslocamento: number
}

export interface EventoDoOrgao {
  situacao: SituacaoDoEncaminhamento
  autor: AutorDoEvento
  ocorridoEm: string
  observacao: string | null
  respostaAoCidadao: string | null
  previsao: string | null
  protocoloDoOrgao: string | null
}

export interface OcorrenciaDoOrgao extends OcorrenciaNaFila {
  protocoloDeOrigem: string | null
  situacaoNaFonte: string | null
  justificativa: string | null
  nota: number | null
  protocoloDoOrgao: string | null
  registrosDoMesmoLocal: number
  podeResponder: boolean
  respostasPossiveis: readonly RespostaPossivel[]
  mesmoProblema: readonly MesmoProblema[]
  eventos: readonly EventoDoOrgao[]
}

export interface RespostaComoOrgao {
  situacao: RespostaPossivel
  respostaAoCidadao: string
  observacao: string
  protocoloDoOrgao: string
  previsao: string | null
  tambem: readonly number[]
}

export interface RespostaRegistrada {
  codigo: string
  situacao: SituacaoDoEncaminhamento
  codigosJuntos: readonly string[]
}

export interface ContagemPorRotulo {
  rotulo: string
  quantidade: number
}

export interface PainelDoOrgao {
  hoje: string
  orgao: Orgao
  nomeDoOrgao: string
  indicadores: IndicadoresDoOrgao
  semanas: readonly SemanaDoCiclo[]
  abertasPorBairro: readonly ContagemPorRotulo[]
  resolvidasPorTema: readonly ContagemPorRotulo[]
  maisUrgentes: readonly OcorrenciaNaFila[]
  gruposDoMesmoProblema: readonly GrupoDoMesmoProblema[]
  pessoasComRetorno: number
}

export interface DemandaPorAno {
  ano: number
  fonte: string
  quantidade: number
}

export interface DemandaDoOrgao {
  orgao: Orgao
  nomeDoOrgao: string
  anoInicio: number
  anoFim: number
  nomesNaFonte: readonly string[]
  total: number
  semBairro: number
  porAno: readonly DemandaPorAno[]
  porBairro: readonly ContagemPorRotulo[]
  porTema: readonly ContagemPorRotulo[]
  porSituacao: readonly ContagemPorRotulo[]
}

export const PEDIDO_INICIAL_DA_FILA: PedidoDaFila = {
  aba: 'novas',
  bairro: null,
  categoria: null,
  deslocamento: 0,
}

export function descreverPrazo(diasParaOPrazo: number): string {
  if (diasParaOPrazo === 0) return 'vence hoje'
  if (diasParaOPrazo > 0) return `vence em ${contar(diasParaOPrazo, 'dia', 'dias')}`
  return `venceu há ${contar(-diasParaOPrazo, 'dia', 'dias')}`
}

export const DIAS_DE_ALERTA_DO_PRAZO = 7

export function prazoPedeAtencao(item: Pick<OcorrenciaNaFila, 'atrasado' | 'diasParaOPrazo'>) {
  return item.atrasado || item.diasParaOPrazo <= DIAS_DE_ALERTA_DO_PRAZO
}

export function estaAberta(situacao: SituacaoDoEncaminhamento): boolean {
  return situacao === 'enviado' || situacao === 'recebido'
}

export type MesmoProblemaDoOrgao = MesmoProblema & { id: number; codigo: string }

function eDoProprioOrgao(item: MesmoProblema): item is MesmoProblemaDoOrgao {
  return item.id !== null && item.codigo !== null
}

/** Só as do próprio órgão e ainda abertas podem receber a mesma resposta. */
export function mesmoProblemaQueDaParaJuntar(
  parecidos: readonly MesmoProblema[],
): readonly MesmoProblemaDoOrgao[] {
  return parecidos.filter(eDoProprioOrgao).filter((item) => estaAberta(item.situacao))
}
