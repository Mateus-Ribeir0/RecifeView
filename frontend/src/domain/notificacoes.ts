import { formatarData, isoDaData } from './formatacao'

export interface Notificacao {
  id: number
  titulo: string
  texto: string
  caminho: string
  criadaEm: string
  lida: boolean
}

export interface CaixaDeNotificacoes {
  naoLidas: number
  itens: readonly Notificacao[]
}

export const CAIXA_VAZIA: CaixaDeNotificacoes = { naoLidas: 0, itens: [] }

const MINUTO = 60_000
const HORA = 60 * MINUTO
const DIA = 24 * HORA

export function descreverQuando(iso: string, agora: Date): string {
  const passado = agora.getTime() - new Date(iso).getTime()
  if (passado < MINUTO) return 'agora'
  if (passado < HORA) return `há ${Math.floor(passado / MINUTO)} min`
  if (passado < DIA) return `há ${Math.floor(passado / HORA)} h`
  if (passado < 2 * DIA) return 'ontem'
  return formatarData(isoDaData(new Date(iso)))
}

/** Chegou notificação nova desde a última consulta: as telas do ciclo se recarregam. */
export function chegouNovidade(anterior: CaixaDeNotificacoes, atual: CaixaDeNotificacoes): boolean {
  const ultimaAnterior = anterior.itens[0]?.id ?? 0
  return (atual.itens[0]?.id ?? 0) > ultimaAnterior
}
