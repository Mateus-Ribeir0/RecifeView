import { vi } from 'vitest'

import type { ServicoDeContribuicoes } from '../application/contribuicoes/servico'
import type {
  CatalogoDoFormulario,
  ParParaRevisar,
  ResumoDasContribuicoes,
} from '../domain/contribuicoes'

export const CATALOGO: CatalogoDoFormulario = {
  temas: [
    {
      chave: 'ruas',
      rotulo: 'Ruas e calçadas',
      servicos: [
        { codigo: '131', rotulo: 'Buraco na rua' },
        { codigo: '155', rotulo: 'Calçada quebrada' },
      ],
    },
  ],
  bairros: [{ chave: 'AFOGADOS', nome: 'Afogados', rpa: '5' }],
}

export const RESUMO: ResumoDasContribuicoes = {
  relatos: 4,
  ocorrencias: 3,
  somados: 1,
  aguardandoRevisao: 1,
  prontasParaPacote: 2,
  emPacote: 0,
  naBase: 0,
  retiradas: 0,
  semRetorno: 2,
}

const LADO = {
  id: 'a',
  recebidaEm: '2026-11-05T10:00:00Z',
  servico: 'Buraco na rua',
  bairro: 'Afogados',
  logradouro: 'RUA FICTICIA',
  numero: '100',
  detalhe: null,
  relatos: 1,
}

export const PAR: ParParaRevisar = {
  id: 9,
  pontuacao: 0.84,
  motivos: ['Números próximos', 'Mesmo serviço', '2 dias de diferença'],
  primeiro: LADO,
  segundo: { ...LADO, id: 'b', numero: '110' },
}

export function criarContribuicoesFalsas(
  mudancas: Partial<ServicoDeContribuicoes> = {},
): ServicoDeContribuicoes {
  return {
    catalogo: vi.fn().mockResolvedValue(CATALOGO),
    logradouros: vi.fn().mockResolvedValue(['RUA FICTICIA']),
    enviar: vi.fn().mockResolvedValue('nova'),
    resumo: vi.fn().mockResolvedValue(RESUMO),
    ocorrencias: vi.fn().mockResolvedValue({ itens: [], total: 0 }),
    pares: vi.fn().mockResolvedValue([PAR]),
    decidir: vi.fn().mockResolvedValue(undefined),
    gerarPacote: vi.fn().mockResolvedValue({ id: 12 }),
    ...mudancas,
  }
}
