import { vi } from 'vitest'

import type { ServicoDeAutenticacao } from '../application/autenticacao/servico'
import type { Usuario } from '../domain/usuario'

export const GESTORA: Usuario = {
  id: '6f1c2b8e-0000-4000-8000-000000000001',
  nome: 'Gestora de Teste',
  email: 'gestora@recife.pe.gov.br',
  perfil: 'GESTOR',
  deveTrocarSenha: false,
  bairroOficial: null,
}

export const CIDADA: Usuario = {
  id: '6f1c2b8e-0000-4000-8000-000000000002',
  nome: 'Maria da Silva',
  email: 'maria@exemplo.com',
  perfil: 'CIDADAO',
  deveTrocarSenha: false,
  bairroOficial: 'AFOGADOS',
}

export function criarServicoFalso(
  substituicoes: Partial<ServicoDeAutenticacao> = {},
): ServicoDeAutenticacao {
  return {
    entrar: vi.fn().mockResolvedValue(GESTORA),
    restaurarSessao: vi.fn().mockResolvedValue(null),
    sair: vi.fn().mockResolvedValue(undefined),
    trocarSenha: vi.fn().mockResolvedValue(GESTORA),
    observarPerdaDeSessao: vi.fn().mockReturnValue(() => undefined),
    criarConta: vi.fn().mockResolvedValue('Se o e-mail puder ser usado, enviamos um código.'),
    confirmarEmail: vi.fn().mockResolvedValue(CIDADA),
    reenviarCodigo: vi.fn().mockResolvedValue('Enviamos um novo código.'),
    pedirNovaSenha: vi.fn().mockResolvedValue('Se o e-mail tiver conta, enviamos um código.'),
    criarNovaSenha: vi.fn().mockResolvedValue(undefined),
    atualizarConta: vi.fn().mockResolvedValue(CIDADA),
    excluirConta: vi.fn().mockResolvedValue(undefined),
    ...substituicoes,
  }
}
