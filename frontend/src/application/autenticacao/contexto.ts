import { createContext } from 'react'

import type { Usuario } from '../../domain/usuario'
import type { Credenciais, TrocaDeSenha } from './servico'

export type MotivoDaSaida = 'saiu' | 'sessao-expirada'

export type EstadoDaSessao =
  | { situacao: 'verificando' }
  | { situacao: 'anonima'; motivo: MotivoDaSaida | null }
  | { situacao: 'autenticada'; usuario: Usuario }

export interface Sessao {
  estado: EstadoDaSessao
  entrar(credenciais: Credenciais): Promise<Usuario>
  sair(): Promise<void>
  trocarSenha(troca: TrocaDeSenha): Promise<Usuario>
}

export const ContextoDaSessao = createContext<Sessao | null>(null)
