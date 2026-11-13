import type { EncaminhamentoNaFila } from './encaminhamentos'
export type RetornoAnterior = 'nao_registrou' | 'registrou_sem_retorno' | 'registrou_com_retorno'
export type ResultadoDoEnvio = 'nova' | 'somada' | 'em_conferencia'
export type DecisaoDoPar = 'mesma' | 'diferente'
export type SituacaoDaOcorrencia = 'aberta' | 'em_pacote' | 'na_base' | 'retirada' | 'somada'

export const TAMANHO_MAXIMO_DO_DETALHE = 280
export const TAMANHO_MINIMO_DA_VIA = 3

export interface ServicoDoFormulario {
  codigo: string
  rotulo: string
}

export interface TemaDoFormulario {
  chave: string
  rotulo: string
  servicos: readonly ServicoDoFormulario[]
}

export interface BairroDoFormulario {
  chave: string
  nome: string
  rpa: string
}

export interface CatalogoDoFormulario {
  temas: readonly TemaDoFormulario[]
  bairros: readonly BairroDoFormulario[]
}

export interface RelatoPreenchido {
  chaveDeEnvio: string
  servicoCodigo: string
  bairroOficial: string
  logradouro: string
  numero: string
  detalhe: string
  retorno: RetornoAnterior
  site: string
}

export interface ResumoDasContribuicoes {
  relatos: number
  ocorrencias: number
  somados: number
  aguardandoRevisao: number
  prontasParaPacote: number
  emPacote: number
  naBase: number
  retiradas: number
  semRetorno: number
}

export interface OcorrenciaDoPainel {
  id: string
  recebidaEm: string
  servico: string
  bairro: string
  logradouro: string | null
  numero: string | null
  relatos: number
  semRetorno: number
  situacao: SituacaoDaOcorrencia
  chaveRegistro: string | null
  encaminhamento: EncaminhamentoNaFila | null
}

export interface PaginaDeOcorrencias {
  itens: readonly OcorrenciaDoPainel[]
  total: number
}

export interface LadoDoPar {
  id: string
  recebidaEm: string
  servico: string
  bairro: string
  logradouro: string | null
  numero: string | null
  detalhe: string | null
  relatos: number
}

export interface ParParaRevisar {
  id: number
  pontuacao: number
  motivos: readonly string[]
  primeiro: LadoDoPar
  segundo: LadoDoPar
}

export const ROTULOS_DAS_SITUACOES: Readonly<Record<SituacaoDaOcorrencia, string>> = {
  aberta: 'Pronta para o pacote',
  em_pacote: 'Em pacote',
  na_base: 'No painel',
  retirada: 'Coberta por registro oficial',
  somada: 'Somada a outra',
}

export const OPCOES_DE_RETORNO: readonly { valor: RetornoAnterior; rotulo: string }[] = [
  { valor: 'nao_registrou', rotulo: 'Ainda não registrei em nenhum canal' },
  { valor: 'registrou_sem_retorno', rotulo: 'Já registrei e não tive retorno' },
  { valor: 'registrou_com_retorno', rotulo: 'Já registrei e recebi retorno' },
]

export function descreverEndereco(lado: Pick<LadoDoPar, 'logradouro' | 'numero'>): string {
  if (!lado.logradouro) return 'Endereço já apagado pelo prazo de guarda'
  return lado.numero ? `${lado.logradouro}, ${lado.numero}` : `${lado.logradouro}, sem número`
}

export function podeGerarPacote(resumo: ResumoDasContribuicoes): boolean {
  return resumo.aguardandoRevisao === 0 && resumo.prontasParaPacote > 0
}

export type PassoDoRelato = 'servico' | 'local' | 'envio'
export type CampoDoRelato = 'servico' | 'bairro' | 'logradouro' | 'numero' | 'detalhe' | 'ciente'
export type ErrosDoRelato = Partial<Record<CampoDoRelato, string>>

export interface RascunhoDoRelato {
  servicoCodigo: string
  bairroOficial: string
  logradouro: string
  numero: string
  detalhe: string
  retorno: RetornoAnterior
  ciente: boolean
}

export const PASSOS_DO_RELATO: readonly PassoDoRelato[] = ['servico', 'local', 'envio']

const PASSO_DE_CADA_CAMPO: Readonly<Record<CampoDoRelato, PassoDoRelato>> = {
  servico: 'servico',
  bairro: 'local',
  logradouro: 'local',
  numero: 'local',
  detalhe: 'envio',
  ciente: 'envio',
}

export const RASCUNHO_VAZIO: RascunhoDoRelato = {
  servicoCodigo: '',
  bairroOficial: '',
  logradouro: '',
  numero: '',
  detalhe: '',
  retorno: 'nao_registrou',
  ciente: false,
}

export function errosDoPasso(passo: PassoDoRelato, rascunho: RascunhoDoRelato): ErrosDoRelato {
  if (passo === 'servico') {
    return rascunho.servicoCodigo ? {} : { servico: 'Escolha o que está acontecendo.' }
  }
  if (passo === 'envio') {
    return rascunho.ciente ? {} : { ciente: 'Confirme que leu o aviso para enviar.' }
  }
  const erros: ErrosDoRelato = {}
  if (!rascunho.bairroOficial) erros.bairro = 'Escolha o bairro.'
  if (rascunho.logradouro.trim().length < TAMANHO_MINIMO_DA_VIA) {
    erros.logradouro = 'Informe o nome da rua.'
  }
  return erros
}

export function passoDoCampo(campo: string | null): PassoDoRelato | null {
  return PASSO_DE_CADA_CAMPO[campo as CampoDoRelato] ?? null
}

export function gerarChaveDeEnvio(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('')
}

export function chaveDoNome(nome: string): string {
  return nome.normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase()
}
