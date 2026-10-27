import { vi } from 'vitest'

import type { ServicoDeAutenticacao } from '../application/autenticacao/servico'
import type { Usuario } from '../domain/usuario'

export const GESTORA: Usuario = {
  id: '6f1c2b8e-0000-4000-8000-000000000001',
  nome: 'Gestora de Teste',
  email: 'gestora@recife.pe.gov.br',
  perfil: 'GESTOR',
  deveTrocarSenha: false,
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
    ...substituicoes,
  }
}
