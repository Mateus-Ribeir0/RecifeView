import type { MotivoDaSaida } from '../../application/autenticacao/contexto'

export const ROTA_INICIAL_DO_PAINEL = '/painel'

export interface EstadoDeNavegacao {
  destino?: string
  motivo?: MotivoDaSaida | null
}

export function lerEstadoDeNavegacao(estado: unknown): EstadoDeNavegacao {
  return typeof estado === 'object' && estado !== null ? (estado as EstadoDeNavegacao) : {}
}
