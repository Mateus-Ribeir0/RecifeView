import type {
  AcessoCorporativo,
  DadosDoAcesso,
  ListaDeAcessos,
  NovoAcesso,
} from '../../domain/acessos'

export interface ServicoDeAcessos {
  listar(): Promise<ListaDeAcessos>
  criar(novo: NovoAcesso): Promise<AcessoCorporativo>
  editar(id: string, dados: DadosDoAcesso): Promise<AcessoCorporativo>
  reenviarConvite(id: string): Promise<AcessoCorporativo>
  desativar(id: string): Promise<AcessoCorporativo>
  reativar(id: string): Promise<AcessoCorporativo>
  excluir(id: string): Promise<void>
}
