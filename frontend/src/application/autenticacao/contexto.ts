import { createContext } from 'react'

import type { ConviteDeAcesso } from '../../domain/acessos'
import type { Usuario } from '../../domain/usuario'
import type {
  AceiteDoConvite,
  Credenciais,
  DadosDaConta,
  NovaConta,
  NovaSenhaComCodigo,
  TrocaDeSenha,
} from './servico'

export type MotivoDaSaida = 'saiu' | 'sessao-expirada' | 'conta-excluida'

export type EstadoDaSessao =
  | { situacao: 'verificando' }
  | { situacao: 'anonima'; motivo: MotivoDaSaida | null }
  | { situacao: 'autenticada'; usuario: Usuario }

export interface Sessao {
  estado: EstadoDaSessao
  entrar(credenciais: Credenciais): Promise<Usuario>
  sair(): Promise<void>
  trocarSenha(troca: TrocaDeSenha): Promise<Usuario>
  atualizarConta(dados: DadosDaConta): Promise<Usuario>
  definirAvisos(recebeAvisos: boolean): Promise<Usuario>
  excluirConta(senha: string): Promise<void>
  criarConta(conta: NovaConta): Promise<Usuario>
  pedirNovaSenha(email: string): Promise<string>
  criarNovaSenha(pedido: NovaSenhaComCodigo): Promise<void>
  abrirConvite(token: string): Promise<ConviteDeAcesso>
  aceitarConvite(aceite: AceiteDoConvite): Promise<Usuario>
}

export const ContextoDaSessao = createContext<Sessao | null>(null)
