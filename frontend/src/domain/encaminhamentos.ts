import { formatarNumero, formatarPorcentagem } from './formatacao'

export type Orgao =
  | 'EMLURB'
  | 'COMPESA'
  | 'NEOENERGIA'
  | 'CTTU'
  | 'DEFESA_CIVIL'
  | 'SEINFRA'
  | 'URB'
  | 'SAUDE'
  | 'MEIO_AMBIENTE'
  | 'ORDEM_PUBLICA'

export type SituacaoDoEncaminhamento = 'enviado' | 'falhou' | 'recebido' | 'resolvido' | 'devolvido'
export type RespostaPossivel = 'recebido' | 'resolvido' | 'devolvido'
export type CanalDeEnvio = 'local' | 'email' | 'webhook'
export type MotivoDaSugestao = 'apontado_no_registro' | 'mais_citado_no_tema' | 'sem_sugestao'
export type AutorDoEvento = 'gestao' | 'orgao' | 'sistema'

export interface OrgaoDoCatalogo {
  orgao: Orgao
  nome: string
  foraDaPrefeitura: boolean
  canal: CanalDeEnvio
}

export interface OcorrenciaEncaminhavel {
  chaveRegistro: string
  fonte: string
  dataAbertura: string | null
  categoria: string | null
  servico: string | null
  bairroOficial: string | null
  rpa: string | null
  situacao: string | null
  orgao: string | null
  protocolo: string | null
}

export interface EventoDoEncaminhamento {
  situacao: SituacaoDoEncaminhamento
  autor: AutorDoEvento
  ocorridoEm: string
  observacao?: string | null
  protocoloDoOrgao?: string | null
}

export interface Encaminhamento {
  id: number
  codigo: string
  ocorrencia: OcorrenciaEncaminhavel
  orgao: Orgao
  nomeDoOrgao: string
  orgaoSugerido: Orgao | null
  nomeDoOrgaoSugerido: string | null
  canal: CanalDeEnvio
  situacao: SituacaoDoEncaminhamento
  atrasado: boolean
  criadoEm: string
  prazoDeResposta: string
  atualizadoEm: string
  nota: number | null
  justificativa: string | null
  automatico: boolean
  protocoloDoOrgao: string | null
  eventos: readonly EventoDoEncaminhamento[]
}

export interface EncaminhamentoNaFila {
  id: number
  codigo: string
  orgao: Orgao
  nomeDoOrgao: string
  situacao: SituacaoDoEncaminhamento
}

export interface Participacao {
  orgao: Orgao
  nome: string
  indicacoes: number
  pct: number
}

export interface SugestaoDeDestino {
  orgao: Orgao | null
  motivo: MotivoDaSugestao
  tema: string | null
  indicacoesDoTema: number
  participacoes: readonly Participacao[]
}

export interface PreparoDoEncaminhamento {
  ocorrencia: OcorrenciaEncaminhavel
  sugestao: SugestaoDeDestino
  orgaos: readonly OrgaoDoCatalogo[]
  encaminhamentos: readonly Encaminhamento[]
  podeEncaminhar: boolean
}

export interface ResumoDosEncaminhamentos {
  total: number
  abertos: number
  atrasados: number
  porSituacao: Partial<Record<SituacaoDoEncaminhamento, number>>
  medianaDeDiasAteResolver: number | null
}

export interface QuadroDeEncaminhamentos {
  hoje: string
  resumo: ResumoDosEncaminhamentos
  itens: readonly Encaminhamento[]
  total: number
}

export interface FiltroDeEncaminhamentos {
  situacao: SituacaoDoEncaminhamento | null
  orgao: Orgao | null
  soAtrasados: boolean
  deslocamento: number
}

export interface PedidoDeEncaminhamento {
  chaveRegistro: string
  orgao: Orgao
  justificativa: string
  nota: number | null
}

export interface RespostaAoEncaminhamento {
  situacao: RespostaPossivel
  protocoloDoOrgao: string
  observacao: string
}

export interface EncaminhamentoParaOOrgao {
  codigo: string
  orgao: Orgao
  nomeDoOrgao: string
  ocorrencia: OcorrenciaEncaminhavel
  situacao: SituacaoDoEncaminhamento
  criadoEm: string
  prazoDeResposta: string
  justificativa: string | null
  protocoloDoOrgao: string | null
  respostasPossiveis: readonly RespostaPossivel[]
  eventos: readonly EventoDoEncaminhamento[]
}

export const FILTRO_INICIAL_DE_ENCAMINHAMENTOS: FiltroDeEncaminhamentos = {
  situacao: null,
  orgao: null,
  soAtrasados: false,
  deslocamento: 0,
}

export const ROTULOS_DAS_SITUACOES: Readonly<Record<SituacaoDoEncaminhamento, string>> = {
  enviado: 'Enviado, sem resposta',
  falhou: 'Falha no envio',
  recebido: 'Recebido pelo órgão',
  resolvido: 'Resolvido',
  devolvido: 'Devolvido pelo órgão',
}

export const ROTULOS_DAS_RESPOSTAS: Readonly<Record<RespostaPossivel, string>> = {
  recebido: 'Recebemos e vamos tratar',
  resolvido: 'Resolvido',
  devolvido: 'Não é com o nosso órgão',
}

export const ROTULOS_DOS_CANAIS: Readonly<Record<CanalDeEnvio, string>> = {
  local: 'caixa de saída local',
  email: 'e-mail',
  webhook: 'sistema do órgão',
}

export const ROTULOS_DOS_AUTORES: Readonly<Record<AutorDoEvento, string>> = {
  gestao: 'pela gestão',
  orgao: 'pelo órgão',
  sistema: 'pelo sistema',
}

export const SITUACOES_DO_FILTRO: readonly SituacaoDoEncaminhamento[] = [
  'enviado',
  'recebido',
  'resolvido',
  'devolvido',
  'falhou',
]

const RESPOSTAS_POR_SITUACAO: Readonly<
  Record<SituacaoDoEncaminhamento, readonly RespostaPossivel[]>
> = {
  enviado: ['recebido', 'resolvido', 'devolvido'],
  recebido: ['resolvido', 'devolvido'],
  falhou: [],
  resolvido: [],
  devolvido: [],
}

export function respostasPossiveis(
  situacao: SituacaoDoEncaminhamento,
): readonly RespostaPossivel[] {
  return RESPOSTAS_POR_SITUACAO[situacao]
}

export function podeReenviar(encaminhamento: Encaminhamento): boolean {
  return encaminhamento.situacao === 'falhou'
}

export function explicarSugestao(sugestao: SugestaoDeDestino): string {
  const lider = sugestao.participacoes[0]
  const evidencia =
    lider && sugestao.tema
      ? ` Nas ${formatarNumero(sugestao.indicacoesDoTema)} indicações da Câmara sobre ${sugestao.tema.toLowerCase()}, ${formatarPorcentagem(lider.pct, 1)} citam ${lider.nome}.`
      : ''
  if (sugestao.motivo === 'apontado_no_registro') {
    return `O próprio registro aponta este órgão.${evidencia}`
  }
  if (sugestao.motivo === 'mais_citado_no_tema') {
    return `É o órgão mais citado no tema.${evidencia}`
  }
  return 'Sem sugestão: o registro não aponta órgão e o tema tem poucas indicações na Câmara. Escolha o órgão.'
}
