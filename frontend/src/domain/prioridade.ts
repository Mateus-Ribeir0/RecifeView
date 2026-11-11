import type { EncaminhamentoNaFila } from './encaminhamentos'

export type ChaveDoCriterio = 'risco' | 'vulnerabilidade' | 'atraso' | 'reincidencia'
export type FonteDaFila = '156' | 'camara' | 'ouvidoria'

export const CHAVES_DOS_CRITERIOS: readonly ChaveDoCriterio[] = [
  'risco',
  'vulnerabilidade',
  'atraso',
  'reincidencia',
]

export const NOTA_ALTA = 7
export const NOTA_MAXIMA = 10

// Escala de Saaty em posições do controle: à esquerda pesa o segundo critério, à direita o primeiro.
export const OPCOES_DA_ESCALA: readonly number[] = [
  -9, -8, -7, -6, -5, -4, -3, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9,
]

export interface Criterio {
  chave: ChaveDoCriterio
  nome: string
  unidade: string
  descricao: string
}

export interface Julgamento {
  primeiro: ChaveDoCriterio
  segundo: ChaveDoCriterio
  valor: number
}

export interface Criterios {
  criterios: readonly Criterio[]
  julgamentosPadrao: readonly Julgamento[]
  razaoAceitavel: number
}

export interface BairroPriorizado {
  bairroOficial: string
  nome: string
  rpa: string
  indice: number
  posicao: number
  contribuicoes: Readonly<Record<ChaveDoCriterio, number>>
  risco: number | null
  vulnerabilidade: number | null
  atraso: number | null
  reincidencia: number | null
}

export interface TesteDeSensibilidade {
  criterio: string
  fator: number
  pesoTestado: number
  mantidosNoTop: number
}

export interface Prioridade {
  pesos: Readonly<Record<ChaveDoCriterio, number>>
  razaoDeConsistencia: number
  coerente: boolean
  bairros: readonly BairroPriorizado[]
  sensibilidade: readonly TesteDeSensibilidade[]
}

export interface OcorrenciaClassificada {
  chaveRegistro: string | null
  encaminhamento: EncaminhamentoNaFila | null
  fila: number
  indice: number
  notas: Readonly<Record<ChaveDoCriterio, number | null>>
  contribuicoes: Readonly<Record<ChaveDoCriterio, number>>
  dataAbertura: string | null
  idadeDias: number
  prazoTipicoDias: number | null
  pedidosAnteriores: number | null
  bairroOficial: string | null
  rpa: string | null
  categoria: string | null
  servico: string | null
  situacao: string | null
  orgao: string | null
  canal: string | null
  dataEnvio: string | null
  dataPrazo: string | null
  natureza: string | null
  diasAlemDoPrazo: number | null
}

export interface FaixaDeNota {
  inicio: number
  fim: number
  registros: number
}

export interface FilaClassificada {
  fonte: FonteDaFila
  registrosNaBase: number
  emAberto: number
  classificados: number
  comNotaAlta: number
  pctNotaAlta: number | null
  amostra: readonly OcorrenciaClassificada[]
  topo: readonly OcorrenciaClassificada[]
  distribuicao: readonly FaixaDeNota[]
}

export type Comparacoes = Readonly<Record<string, number>>

export function chaveDoPar(primeiro: ChaveDoCriterio, segundo: ChaveDoCriterio): string {
  return `${primeiro}|${segundo}`
}

export function valorDaOpcao(opcao: number): number {
  return opcao > 0 ? opcao : 1 / -opcao
}

export function opcaoDoValor(valor: number): number {
  return valor >= 1 ? Math.round(valor) : -Math.round(1 / valor)
}

export function rotuloDaOpcao(opcao: number, primeiro: string, segundo: string): string {
  if (opcao === 1) return 'igual importância'
  return opcao > 0 ? `${primeiro} ${opcao}× mais` : `${segundo} ${-opcao}× mais`
}
