export type ModoDaWarRoom = 'hoje' | 'dia' | 'simulacao' | 'fim'

export interface CalendarioDaWarRoom {
  hoje: string
  primeiroDia: string
  ultimoDia: string
  ultimoRegistro156: string | null
  ultimoRegistroOuvidoria: string | null
  segundosPorDia: number
  diasSimulados: number
}

export interface EntradasDoDia {
  entradas: number
  atendidos: number
  mediaDoDiaDaSemana: number
  camara: number
  ouvidoria: number
  defesaCivil: number
}

export interface EstoqueDoDia {
  abertos: number
  atrasados: number
  classificaveis: number
  prioritarios: number
  comNotaMuitoAlta: number
  camara: {
    total: number
    medianaDeDias: number | null
    temaComMais: string | null
    temaQuantidade: number
  }
  ouvidoria: {
    total: number
    medianaDeDias: number | null
    orgaoComMais: string | null
    orgaoQuantidade: number
  }
  entradasNosUltimos30: number
  entradasNos30Anteriores: number
  fimDaJanela: string
}

export interface FilaDoDia {
  nota: number
  servico: string | null
  bairroOficial: string | null
  idadeDias: number
  pedidosAnteriores: number | null
}

export interface DiaDaSerie {
  data: string
  entradas: number
  atendidos: number
}

export interface QuadroDoDia {
  dia: string
  entradas: EntradasDoDia | null
  estoque: EstoqueDoDia
  atrasoPorBairro: readonly { bairroOficial: string; atrasados: number }[]
  fila: readonly FilaDoDia[]
  serie: readonly DiaDaSerie[]
  categorias: readonly { categoria: string; abertos: number; atrasados: number }[]
  categoriasDoDia: readonly { nome: string; n: number }[]
  bairrosDoDia: readonly { nome: string; n: number }[]
}

export function somarDias(iso: string, dias: number): string {
  const data = new Date(`${iso}T00:00:00Z`)
  data.setUTCDate(data.getUTCDate() + dias)
  return data.toISOString().slice(0, 10)
}

export function diasEntre(inicio: string, fim: string): number {
  const milissegundosPorDia = 86_400_000
  return Math.round((Date.parse(fim) - Date.parse(inicio)) / milissegundosPorDia)
}
