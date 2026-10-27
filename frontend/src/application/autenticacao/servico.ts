import type { Usuario } from '../../domain/usuario'

export interface Credenciais {
  email: string
  senha: string
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
}
