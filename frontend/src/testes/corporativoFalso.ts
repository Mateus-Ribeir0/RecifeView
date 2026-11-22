import { vi } from 'vitest'

import type { ServicoDeAcessos } from '../application/acessos/servico'
import type { ServicoDoOrgao } from '../application/corporativo/servico'
import type { ServicoDeNotificacoes } from '../application/notificacoes/servico'
import type { AcessoCorporativo } from '../domain/acessos'
import type { OcorrenciaDoOrgao, OcorrenciaNaFila, PainelDoOrgao } from '../domain/corporativo'
import type { CaixaDeNotificacoes } from '../domain/notificacoes'

export const NA_FILA: OcorrenciaNaFila = {
  id: 7,
  codigo: 'ENC-2026-000007',
  fonte: '156_EMLURB',
  categoria: 'DRENAGEM',
  servico: 'LIMPEZA DE GALERIAS',
  bairroOficial: 'AFOGADOS',
  rpa: '5',
  localAproximado: null,
  dataAbertura: '2026-11-02',
  situacao: 'enviado',
  atrasado: false,
  criadoEm: '2026-11-03T12:00:00Z',
  prazoDeResposta: '2026-12-03',
  diasParaOPrazo: 14,
  previsao: null,
  respostaAoCidadao: null,
  mesmoProblemaNoOrgao: 1,
  mesmoProblemaEmOutrosOrgaos: 0,
  pessoasQueAcompanham: 2,
}

export const OCORRENCIA_DO_ORGAO: OcorrenciaDoOrgao = {
  ...NA_FILA,
  protocoloDeOrigem: null,
  situacaoNaFonte: 'ABERTA',
  justificativa: 'Terceiro pedido no mesmo ponto',
  nota: 8.2,
  protocoloDoOrgao: null,
  registrosDoMesmoLocal: 3,
  podeResponder: true,
  respostasPossiveis: ['recebido', 'resolvido', 'devolvido'],
  mesmoProblema: [
    {
      id: 8,
      codigo: 'ENC-2026-000008',
      orgao: 'COMPESA',
      nomeDoOrgao: 'Compesa',
      situacao: 'enviado',
      atrasado: false,
      dataAbertura: '2026-11-03',
      certo: true,
      motivos: ['Mesmo endereço', 'Mesmo serviço', '1 dia de diferença'],
    },
    {
      id: null,
      codigo: null,
      orgao: 'EMLURB',
      nomeDoOrgao: 'Emlurb',
      situacao: 'recebido',
      atrasado: false,
      dataAbertura: '2026-11-04',
      certo: false,
      motivos: ['Mesmo endereço'],
    },
  ],
  eventos: [
    {
      situacao: 'enviado',
      autor: 'gestao',
      ocorridoEm: '2026-11-03T12:00:00Z',
      observacao: null,
      respostaAoCidadao: null,
      previsao: null,
      protocoloDoOrgao: null,
    },
  ],
}

export const PAINEL: PainelDoOrgao = {
  hoje: '2026-11-19',
  orgao: 'COMPESA',
  nomeDoOrgao: 'Compesa',
  indicadores: {
    orgao: 'COMPESA',
    nomeDoOrgao: 'Compesa',
    encaminhados: 3,
    falhas: 0,
    abertas: 2,
    novas: 2,
    emAtendimento: 0,
    vencidas: 0,
    resolvidas: 1,
    resolvidasNoPrazo: 1,
    pctNoPrazo: 100,
    resolvidasEm30Dias: 1,
    devolvidas: 0,
    medianaDeDiasAteResolver: 4,
    voltaramASerPedidas: 0,
  },
  semanas: [{ inicio: '2026-11-16', recebidas: 3, resolvidas: 1 }],
  abertasPorBairro: [{ rotulo: 'AFOGADOS', quantidade: 2 }],
  resolvidasPorTema: [{ rotulo: 'DRENAGEM', quantidade: 1 }],
  maisUrgentes: [NA_FILA],
  gruposDoMesmoProblema: [],
  pessoasComRetorno: 2,
}

export function criarOrgaoFalso(substituicoes: Partial<ServicoDoOrgao> = {}): ServicoDoOrgao {
  return {
    painel: vi.fn().mockResolvedValue(PAINEL),
    fila: vi.fn().mockResolvedValue({
      hoje: '2026-11-19',
      itens: [NA_FILA],
      total: 1,
      porAba: {
        novas: 1,
        em_atendimento: 0,
        vencidas: 0,
        resolvidas: 0,
        devolvidas: 0,
        todas: 1,
      },
      bairros: ['AFOGADOS'],
      categorias: ['DRENAGEM'],
    }),
    ocorrencia: vi.fn().mockResolvedValue(OCORRENCIA_DO_ORGAO),
    responder: vi.fn().mockResolvedValue({
      codigo: 'ENC-2026-000007',
      situacao: 'resolvido',
      codigosJuntos: ['ENC-2026-000008'],
    }),
    dados: vi.fn(),
    ...substituicoes,
  }
}

export const ACESSO: AcessoCorporativo = {
  id: 'f0c1b2a3-0000-4000-8000-000000000010',
  nome: 'Ana Souza',
  email: 'ana@compesa.exemplo',
  orgao: 'COMPESA',
  nomeDoOrgao: 'Compesa',
  situacao: 'convite_enviado',
  criadoEm: '2026-11-18T12:00:00Z',
  conviteExpiraEm: '2026-11-25T12:00:00Z',
  ultimoAcessoEm: null,
}

export function criarAcessosFalsos(
  substituicoes: Partial<ServicoDeAcessos> = {},
): ServicoDeAcessos {
  return {
    listar: vi.fn().mockResolvedValue({ podeAlterar: true, itens: [ACESSO] }),
    criar: vi.fn().mockResolvedValue(ACESSO),
    editar: vi.fn().mockResolvedValue(ACESSO),
    reenviarConvite: vi.fn().mockResolvedValue(ACESSO),
    desativar: vi.fn().mockResolvedValue({ ...ACESSO, situacao: 'desativado' }),
    reativar: vi.fn().mockResolvedValue(ACESSO),
    excluir: vi.fn().mockResolvedValue(undefined),
    ...substituicoes,
  }
}

export const CAIXA: CaixaDeNotificacoes = {
  naoLidas: 1,
  itens: [
    {
      id: 2,
      titulo: 'Andamento: Compesa',
      texto: 'O seu pedido foi resolvido, segundo Compesa.',
      caminho: '/cidade/meus-pedidos',
      criadaEm: '2026-11-19T11:00:00Z',
      lida: false,
    },
  ],
}

export function criarNotificacoesFalsas(
  substituicoes: Partial<ServicoDeNotificacoes> = {},
): ServicoDeNotificacoes {
  return {
    caixa: vi.fn().mockResolvedValue(CAIXA),
    marcarComoLida: vi.fn().mockResolvedValue(undefined),
    marcarTodasComoLidas: vi.fn().mockResolvedValue(undefined),
    ...substituicoes,
  }
}
