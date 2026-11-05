import type { Filtros } from '../../domain/filtros'
import type {
  CanaisDaOuvidoria,
  CatalogoDeFiltros,
  Consulta,
  Prazos,
  Recorrencias,
  Retorno,
  SobreOsDados,
  Territorio,
  VisaoGeral,
} from '../../domain/painel'
import type {
  Criterios,
  FilaClassificada,
  FonteDaFila,
  Julgamento,
  Prioridade,
} from '../../domain/prioridade'
import type { CalendarioDaWarRoom, QuadroDoDia } from '../../domain/warRoom'

export interface PedidoDeFila {
  fonte: FonteDaFila
  julgamentos: readonly Julgamento[]
  semente: number
  filtros: Filtros
}

export interface ServicoDoPainel {
  catalogo(): Promise<CatalogoDeFiltros>
  visaoGeral(filtros: Filtros): Promise<Consulta<VisaoGeral>>
  retorno(filtros: Filtros): Promise<Consulta<Retorno>>
  ouvidoria(filtros: Filtros): Promise<Consulta<CanaisDaOuvidoria>>
  recorrencias(filtros: Filtros, semGenerico: boolean): Promise<Consulta<Recorrencias>>
  prazos(filtros: Filtros, semMesmoDia: boolean): Promise<Consulta<Prazos>>
  territorio(filtros: Filtros): Promise<Consulta<Territorio>>
  criterios(): Promise<Criterios>
  prioridade(julgamentos: readonly Julgamento[]): Promise<Prioridade>
  fila(pedido: PedidoDeFila): Promise<FilaClassificada>
  calendario(): Promise<CalendarioDaWarRoom>
  quadroDoDia(dia: string, inicioDaSerie: string | null): Promise<QuadroDoDia>
  sobre(): Promise<SobreOsDados>
}
