import type {
  DemandaDoOrgao,
  FilaDoOrgao,
  OcorrenciaDoOrgao,
  PainelDoOrgao,
  PedidoDaFila,
  RespostaComoOrgao,
  RespostaRegistrada,
} from '../../domain/corporativo'

export interface PeriodoDosDados {
  anoInicio: number
  anoFim: number
}

export interface ServicoDoOrgao {
  painel(): Promise<PainelDoOrgao>
  fila(pedido: PedidoDaFila): Promise<FilaDoOrgao>
  ocorrencia(id: number): Promise<OcorrenciaDoOrgao>
  responder(id: number, resposta: RespostaComoOrgao): Promise<RespostaRegistrada>
  dados(periodo: PeriodoDosDados): Promise<DemandaDoOrgao>
}
