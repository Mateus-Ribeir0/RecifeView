import type { AreaDeAcesso, Usuario } from '../../domain/usuario'

export interface Credenciais {
  email: string
  senha: string
  area?: AreaDeAcesso
}

export interface NovaConta {
  nome: string
  email: string
  senha: string
  bairroOficial: string | null
  aceitouOsTermos: boolean
  site: string
}

export interface NovaSenhaComCodigo {
  email: string
  codigo: string
  novaSenha: string
}

export interface DadosDaConta {
  nome: string
  bairroOficial: string | null
}

export interface TrocaDeSenha {
  senhaAtual: string
  novaSenha: string
}

export interface ServicoDeAutenticacao {
  entrar(credenciais: Credenciais): Promise<Usuario>
  restaurarSessao(): Promise<Usuario | null>
  sair(): Promise<void>
  trocarSenha(troca: TrocaDeSenha): Promise<Usuario>
  observarPerdaDeSessao(aoPerder: () => void): () => void
  criarConta(conta: NovaConta): Promise<Usuario>
  pedirNovaSenha(email: string): Promise<string>
  criarNovaSenha(pedido: NovaSenhaComCodigo): Promise<void>
  atualizarConta(dados: DadosDaConta): Promise<Usuario>
  definirAvisos(recebeAvisos: boolean): Promise<Usuario>
  excluirConta(senha: string): Promise<void>
}
