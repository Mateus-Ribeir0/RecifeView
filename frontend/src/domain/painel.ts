export interface Meta {
  fonte: readonly string[]
  periodo: { inicio: number; fim: number }
  n: number
  atualizadoEm: string | null
}

export interface Consulta<T> {
  dados: T
  meta: Meta
}

export interface BairroDoCatalogo {
  bairroOficial: string
  nome: string
  rpa: string
  populacao: number
  pctFavela: number
  taxaConfiavel: boolean
}

export interface FonteDoCatalogo {
  codigo: string
  rotulo: string
  registros: number
}

export interface CatalogoDeFiltros {
  anoMinimo: number
  anoMaximo: number
  rpas: readonly string[]
  bairros: readonly BairroDoCatalogo[]
  categorias: readonly string[]
  fontes: readonly FonteDoCatalogo[]
}

export interface DemandaPorAno {
  ano: number
  fonte: string
  n: number
}

export interface ResumoDasIndicacoes {
  total: number
  enviadas: number
  respondidas: number
  pctEnviadas: number | null
  pctRespondidas: number | null
  medianaDiasAteEnvio: number | null
  medianaDiasAteResposta: number | null
}

export interface VisaoGeral {
  demandas: number
  indicacoes: ResumoDasIndicacoes
  pctLocalRepetido: number | null
  prazo: { mediana: number | null; p90: number | null }
  serie: readonly DemandaPorAno[]
}

export interface RespostaPorAno {
  ano: number
  indicacoes: number
  respondidas: number
  canal: string | null
  pctRespondidas: number
}

export interface CelulaDeDestino {
  categoria: string
  orgao: string
  n: number
  pct: number
}

export interface DispersaoDaCategoria {
  categoria: string
  orgaoPrincipal: string
  pctPrincipal: number
  orgaos: number
}

export interface FluxoDeOrgao {
  orgao: string
  desfecho: string
  n: number
}

export interface CaminhoDaCategoria {
  categoria: string
  fluxos: readonly FluxoDeOrgao[]
}

export interface Retorno {
  resumo: ResumoDasIndicacoes
  porAno: readonly RespostaPorAno[]
  celulas: readonly CelulaDeDestino[]
  orgaos: readonly string[]
  dispersoes: readonly DispersaoDaCategoria[]
  caminhos: readonly CaminhoDaCategoria[]
}

export interface CanalPorAno {
  ano: number
  canal: string
  n: number
  pct: number
}

export interface CanaisDaOuvidoria {
  canais: readonly CanalPorAno[]
  anoDoApp: number | null
  pctDoApp: number | null
  pctNoPrazo: number | null
  total: number
}

export interface IntervalosDeRepeticao {
  duplicidade: number
  intermediario: number
  reincidencia: number
  total: number
}

export interface RecorrenciaPorCategoria {
  categoria: string
  pedidos: number
  repetidos: number
  pctRepetidos: number
  intervalos: IntervalosDeRepeticao
}

export interface PontoCronico {
  bairroOficial: string | null
  categoria: string | null
  servico: string | null
  pedidos: number
  diasDistintos: number
  primeiroAno: number
  ultimoAno: number
}

export interface Recorrencias {
  pedidos: number
  repetidos: number
  pctRepetidos: number | null
  intervalos: IntervalosDeRepeticao
  pontosCronicos: number
  minimoPorCategoria: number
  porCategoria: readonly RecorrenciaPorCategoria[]
  listaDePontos: readonly PontoCronico[]
}

export interface ResumoDosPrazos {
  pedidos: number
  mediana: number | null
  p90: number | null
  pctMesmoDia: number | null
  pctAcimaDe90Dias: number | null
}

export interface PrazoPorAno {
  ano: number
  mediana: number
  p90: number
}

export interface FaixaDePrazo {
  faixa: string
  n: number
  pct: number
}

export interface PrazoPorCategoria {
  categoria: string
  pedidos: number
  mediana: number
  p90: number
  pctMesmoDia: number
}

export interface EstoquePorCategoria {
  categoria: string
  abertos: number
  acimaDoPrazo: number
}

export interface EstoqueAberto {
  abertos: number
  acimaDoPrazo: number
  pctAcimaDoPrazo: number | null
  porCategoria: readonly EstoquePorCategoria[]
}

export interface Prazos {
  resumo: ResumoDosPrazos
  porAno: readonly PrazoPorAno[]
  faixas: readonly FaixaDePrazo[]
  minimoPorCategoria: number
  porCategoria: readonly PrazoPorCategoria[]
  estoque: EstoqueAberto
}

export interface FaixaDeTaxa {
  inicio: number
  fim: number
}

export interface IndicadorDeTerritorio {
  volume: number
  taxa: number | null
  classe: number | null
}

export interface BairroDoTerritorio {
  bairroOficial: string
  nome: string
  rpa: string
  populacao: number
  pctFavela: number
  taxaConfiavel: boolean
  emDestaque: boolean
  central156: IndicadorDeTerritorio
  defesaCivil: IndicadorDeTerritorio
  pctReincidencia156: number | null
  pctAtraso156: number | null
  abertos156: number | null
}

export interface Ponto {
  x: number
  y: number
}

export interface Territorio {
  bairros: readonly BairroDoTerritorio[]
  faixas156: readonly FaixaDeTaxa[]
  faixasDefesaCivil: readonly FaixaDeTaxa[]
  tendencia156: readonly Ponto[]
  tendenciaDefesaCivil: readonly Ponto[]
  anos156: number
  anosDefesaCivil: number
}

export interface SobreOsDados {
  cobertura: readonly { fonte: string; ano: number; n: number }[]
  correcoes: readonly { correcao: string; registros: number }[]
  registrosNaBase: number
  atualizadoEm: string | null
}
