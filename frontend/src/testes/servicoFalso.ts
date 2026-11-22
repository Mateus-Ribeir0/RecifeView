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
  recebeAvisos: true,
  orgao: null,
  nomeDoOrgao: null,
}

export const CIDADA: Usuario = {
  id: '6f1c2b8e-0000-4000-8000-000000000002',
  nome: 'Maria da Silva',
  email: 'maria@exemplo.com',
  perfil: 'CIDADAO',
  deveTrocarSenha: false,
  bairroOficial: 'AFOGADOS',
  recebeAvisos: true,
  orgao: null,
  nomeDoOrgao: null,
}

export const ADMINISTRADORA: Usuario = {
  ...GESTORA,
  id: '6f1c2b8e-0000-4000-8000-000000000003',
  nome: 'Administração de Teste',
  email: 'administracao@recife.pe.gov.br',
  perfil: 'ADMINISTRADOR',
}

export const EQUIPE_DA_COMPESA: Usuario = {
  id: '6f1c2b8e-0000-4000-8000-000000000004',
  nome: 'Ana Souza',
  email: 'ana@compesa.exemplo',
  perfil: 'CORPORATIVO',
  deveTrocarSenha: false,
  bairroOficial: null,
  recebeAvisos: true,
  orgao: 'COMPESA',
  nomeDoOrgao: 'Compesa',
}

export const CONVITE = {
  nome: 'Ana Souza',
  email: 'ana@compesa.exemplo',
  orgao: 'COMPESA' as const,
  nomeDoOrgao: 'Compesa',
  expiraEm: '2026-11-26T12:00:00Z',
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
    criarConta: vi.fn().mockResolvedValue(CIDADA),
    pedirNovaSenha: vi.fn().mockResolvedValue('Se o e-mail tiver conta, enviamos um código.'),
    criarNovaSenha: vi.fn().mockResolvedValue(undefined),
    atualizarConta: vi.fn().mockResolvedValue(CIDADA),
    definirAvisos: vi.fn().mockResolvedValue({ ...CIDADA, recebeAvisos: false }),
    excluirConta: vi.fn().mockResolvedValue(undefined),
    abrirConvite: vi.fn().mockResolvedValue(CONVITE),
    aceitarConvite: vi.fn().mockResolvedValue(EQUIPE_DA_COMPESA),
    ...substituicoes,
  }
}
