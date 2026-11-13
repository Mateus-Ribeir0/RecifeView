import { vi } from 'vitest'

import type {
  ServicoDeEncaminhamentos,
  ServicoDeRetornoDoOrgao,
} from '../application/encaminhamentos/servico'
import type {
  Encaminhamento,
  EncaminhamentoParaOOrgao,
  OcorrenciaEncaminhavel,
  PreparoDoEncaminhamento,
} from '../domain/encaminhamentos'

export const CHAVE_LONGA = '6671749688801546836'

export const OCORRENCIA: OcorrenciaEncaminhavel = {
  chaveRegistro: CHAVE_LONGA,
  fonte: 'CAMARA_REQUERIMENTOS',
  dataAbertura: '2026-09-01',
  categoria: 'DRENAGEM',
  servico: null,
  bairroOficial: 'AFOGADOS',
  rpa: '5',
  situacao: 'ENVIADA',
  orgao: 'COMPESA',
  protocolo: 'TESTE-0001',
  referenciaDeLocal: null,
}

export const PREPARO: PreparoDoEncaminhamento = {
  ocorrencia: OCORRENCIA,
  sugestao: {
    orgao: 'COMPESA',
    motivo: 'apontado_no_registro',
    tema: 'DRENAGEM',
    indicacoesDoTema: 100,
    participacoes: [
      { orgao: 'EMLURB', nome: 'Emlurb', indicacoes: 80, pct: 80 },
      { orgao: 'COMPESA', nome: 'Compesa', indicacoes: 5, pct: 5 },
    ],
  },
  orgaos: [
    { orgao: 'EMLURB', nome: 'Emlurb', foraDaPrefeitura: false, canal: 'local' },
    { orgao: 'COMPESA', nome: 'Compesa', foraDaPrefeitura: true, canal: 'email' },
  ],
  encaminhamentos: [],
  podeEncaminhar: true,
}

export const ENCAMINHAMENTO: Encaminhamento = {
  id: 1,
  codigo: 'ENC-2026-000001',
  ocorrencia: OCORRENCIA,
  orgao: 'COMPESA',
  nomeDoOrgao: 'Compesa',
  orgaoSugerido: 'COMPESA',
  nomeDoOrgaoSugerido: 'Compesa',
  canal: 'email',
  situacao: 'enviado',
  atrasado: false,
  criadoEm: '2026-11-11T15:00:00Z',
  prazoDeResposta: '2026-12-11',
  atualizadoEm: '2026-11-11T15:00:00Z',
  nota: 8.4,
  justificativa: null,
  automatico: false,
  protocoloDoOrgao: null,
  lembreteEnviadoEm: null,
  contribuicaoId: null,
  eventos: [{ situacao: 'enviado', autor: 'gestao', ocorridoEm: '2026-11-11T15:00:00Z' }],
}

export const PARA_O_ORGAO: EncaminhamentoParaOOrgao = {
  codigo: 'ENC-2026-000001',
  orgao: 'COMPESA',
  nomeDoOrgao: 'Compesa',
  ocorrencia: OCORRENCIA,
  situacao: 'enviado',
  criadoEm: '2026-11-11T15:00:00Z',
  prazoDeResposta: '2026-12-11',
  justificativa: 'Terceira indicação no mesmo ponto',
  protocoloDoOrgao: null,
  respostasPossiveis: ['recebido', 'resolvido', 'devolvido'],
  eventos: [{ situacao: 'enviado', autor: 'gestao', ocorridoEm: '2026-11-11T15:00:00Z' }],
}

export function criarEncaminhamentosFalsos(
  substituicoes: Partial<ServicoDeEncaminhamentos> = {},
): ServicoDeEncaminhamentos {
  return {
    orgaos: vi.fn().mockResolvedValue(PREPARO.orgaos),
    preparar: vi.fn().mockResolvedValue(PREPARO),
    encaminhar: vi.fn().mockResolvedValue(ENCAMINHAMENTO),
    listar: vi.fn().mockResolvedValue({
      hoje: '2026-11-11',
      resumo: { total: 1, abertos: 1, atrasados: 0, porSituacao: { enviado: 1 } },
      itens: [ENCAMINHAMENTO],
      total: 1,
    }),
    consultar: vi.fn().mockResolvedValue(ENCAMINHAMENTO),
    registrarRetorno: vi.fn().mockResolvedValue({ ...ENCAMINHAMENTO, situacao: 'recebido' }),
    reenviar: vi.fn().mockResolvedValue(ENCAMINHAMENTO),
    pendencias: vi.fn().mockResolvedValue({
      devolvidos: 1,
      falhas: 0,
      prazoVencido: 2,
      pedemAcao: 3,
      duplasNoPenteFino: 4,
    }),
    ...substituicoes,
  }
}

export function criarRetornoFalso(
  substituicoes: Partial<ServicoDeRetornoDoOrgao> = {},
): ServicoDeRetornoDoOrgao {
  return {
    abrir: vi.fn().mockResolvedValue(PARA_O_ORGAO),
    responder: vi
      .fn()
      .mockResolvedValue({ ...PARA_O_ORGAO, situacao: 'resolvido', respostasPossiveis: [] }),
    ...substituicoes,
  }
}
