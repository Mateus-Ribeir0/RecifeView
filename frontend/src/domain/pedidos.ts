import type { Orgao, SituacaoDoEncaminhamento } from './encaminhamentos'

const TAMANHO_MINIMO_DO_PROTOCOLO = 4
const TAMANHO_MAXIMO_DO_PROTOCOLO = 40
const FORMATO_DO_PROTOCOLO = /^[A-Z0-9./-]+$/

export interface EtapaPublica {
  situacao: SituacaoDoEncaminhamento
  ocorridoEm: string
}

export interface EncaminhamentoPublico {
  codigo: string
  orgao: Orgao
  nomeDoOrgao: string
  situacao: SituacaoDoEncaminhamento
  atrasado: boolean
  encaminhadoEm: string
  prazoDeResposta: string
  protocoloDoOrgao: string | null
  etapas: readonly EtapaPublica[]
}

export interface AndamentoDoPedido {
  fonte: string
  rotuloDaFonte: string
  protocolo: string
  dataAbertura: string | null
  categoria: string | null
  servico: string | null
  tipoRegistro: string | null
  orgao: string | null
  situacao: string | null
  dataUltMovimento: string | null
  prazoDaFonte: string | null
  bairroOficial: string | null
  rpa: string | null
  encaminhamentos: readonly EncaminhamentoPublico[]
}

export interface PedidoAcompanhado {
  id: number
  protocolo: string
  criadoEm: string
  andamentos: readonly AndamentoDoPedido[]
}

export function normalizarProtocolo(texto: string): string {
  return texto.replace(/\s+/g, '').toUpperCase()
}

export function protocoloEValido(texto: string): boolean {
  const protocolo = normalizarProtocolo(texto)
  return (
    protocolo.length >= TAMANHO_MINIMO_DO_PROTOCOLO &&
    protocolo.length <= TAMANHO_MAXIMO_DO_PROTOCOLO &&
    FORMATO_DO_PROTOCOLO.test(protocolo)
  )
}

export function encaminhamentoAtual(andamento: AndamentoDoPedido): EncaminhamentoPublico | null {
  return andamento.encaminhamentos[0] ?? null
}
