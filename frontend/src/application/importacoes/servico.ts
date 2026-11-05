import type {
  CampoDaBase,
  DetalheDaImportacao,
  EscolhaDeColunas,
  FiltroDoHistorico,
  PaginaDeImportacoes,
  PaginaDeRegistros,
  RespostasDePendencias,
  ResumoDaImportacao,
} from '../../domain/importacoes'

export interface ServicoDeImportacoes {
  campos(): Promise<readonly CampoDaBase[]>
  listar(filtro: FiltroDoHistorico): Promise<PaginaDeImportacoes>
  enviar(arquivo: File): Promise<ResumoDaImportacao>
  consultar(id: number): Promise<DetalheDaImportacao>
  definirColunas(id: number, escolha: EscolhaDeColunas): Promise<ResumoDaImportacao>
  responderPendencias(id: number, respostas: RespostasDePendencias): Promise<ResumoDaImportacao>
  confirmar(id: number): Promise<ResumoDaImportacao>
  cancelar(id: number): Promise<ResumoDaImportacao>
  desfazer(id: number): Promise<ResumoDaImportacao>
  registros(id: number, deslocamento: number): Promise<PaginaDeRegistros>
}
