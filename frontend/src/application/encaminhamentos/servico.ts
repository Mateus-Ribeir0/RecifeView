import type {
  Encaminhamento,
  EncaminhamentoParaOOrgao,
  FiltroDeEncaminhamentos,
  OrgaoDoCatalogo,
  PendenciasDoPainel,
  PedidoDeEncaminhamento,
  PreparoDoEncaminhamento,
  QuadroDeEncaminhamentos,
  RespostaAoEncaminhamento,
} from '../../domain/encaminhamentos'

export interface ServicoDeEncaminhamentos {
  orgaos(): Promise<readonly OrgaoDoCatalogo[]>
  preparar(chaveRegistro: string): Promise<PreparoDoEncaminhamento>
  encaminhar(pedido: PedidoDeEncaminhamento): Promise<Encaminhamento>
  listar(filtro: FiltroDeEncaminhamentos): Promise<QuadroDeEncaminhamentos>
  consultar(id: number): Promise<Encaminhamento>
  registrarRetorno(id: number, resposta: RespostaAoEncaminhamento): Promise<Encaminhamento>
  reenviar(id: number): Promise<Encaminhamento>
  pendencias(): Promise<PendenciasDoPainel>
}

export interface ServicoDeRetornoDoOrgao {
  abrir(token: string): Promise<EncaminhamentoParaOOrgao>
  responder(token: string, resposta: RespostaAoEncaminhamento): Promise<EncaminhamentoParaOOrgao>
}
