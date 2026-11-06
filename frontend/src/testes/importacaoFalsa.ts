import { vi } from 'vitest'

import type { ServicoDeImportacoes } from '../application/importacoes/servico'
import type { DetalheDaImportacao, ResultadoDaCarga } from '../domain/importacoes'

const RESULTADO_VAZIO: ResultadoDaCarga = {
  lidas: 0,
  aceitas: 0,
  novas: 0,
  atualizadas: 0,
  iguais: 0,
  ignoradas: 0,
  retiradas: 0,
  repetidasNoArquivo: 0,
  semIdLocal: 0,
  descartes: {},
  correcoes: {},
  fontes: {},
  penteFino: {},
}

export function criarImportacao(mudancas: Partial<DetalheDaImportacao> = {}): DetalheDaImportacao {
  return {
    id: 7,
    nomeDoArquivo: '156_2026.csv',
    tamanhoEmBytes: 2048,
    status: 'AGUARDANDO_COLUNAS',
    progresso: 0,
    fonte: '156_EMLURB',
    layout: 'portal_156',
    dataDoRetrato: '2026-11-05',
    periodoInicio: null,
    periodoFim: null,
    criadaEm: '2026-11-05T10:00:00Z',
    concluidaEm: null,
    desfeitaEm: null,
    nomeDeQuemImportou: 'Gestora de Demonstração',
    cargaInicial: false,
    arquivoGuardado: true,
    resultado: RESULTADO_VAZIO,
    estrutura: {
      formato: 'csv',
      codificacao: 'utf-8-sig',
      separador: ';',
      layoutNome: '156 / Emlurb, Portal de Dados Abertos',
      guardarArquivo: false,
      mesmoArquivo: [],
      colunas: [
        {
          nome: 'DATA_DEMANDA',
          campo: 'data_abertura',
          origem: 'layout',
          bloqueada: false,
          motivoDeBloqueio: null,
          exemplos: ['2026-02-10'],
        },
        {
          nome: 'GRUPO',
          campo: 'categoria',
          origem: 'sinonimo',
          bloqueada: false,
          motivoDeBloqueio: null,
          exemplos: ['DRENAGEM'],
        },
        {
          nome: 'CPF',
          campo: null,
          origem: 'bloqueada',
          bloqueada: true,
          motivoDeBloqueio: 'Documento pessoal',
          exemplos: [],
        },
      ],
    },
    decisoes: {
      fonte: '156_EMLURB',
      dataDoRetrato: '2026-11-05',
      mapeamento: {},
      valoresFixos: {},
      formatoDeData: null,
      substituicoes: {},
      padraoParaValores: {},
      datasInvalidas: null,
      repetidosNaBase: null,
      repetidosNoArquivo: null,
      coincidenciasCertas: null,
      coincidenciasProvaveis: null,
    },
    pendencias: {
      itens: [],
      previa: [],
      resumo: {
        lidas: 10,
        aceitas: 9,
        novas: 7,
        iguais: 1,
        alteradas: 1,
        repetidasNoArquivo: 0,
        semIdLocal: 0,
        periodoInicio: '2026-01-01',
        periodoFim: '2026-02-01',
        descartes: { linha_quebrada: 1 },
        correcoes: {},
        fontes: { '156_EMLURB': 9 },
        penteFino: {},
      },
    },
    mensagemDeErro: null,
    podeDesfazer: false,
    ...mudancas,
  }
}

export function criarServicoDeImportacoesFalso(): ServicoDeImportacoes {
  const importacao = criarImportacao()
  return {
    campos: vi.fn().mockResolvedValue([
      { nome: 'data_abertura', rotulo: 'Data de abertura', tipo: 'data', descricao: '' },
      { nome: 'categoria', rotulo: 'Categoria', tipo: 'texto', descricao: '' },
    ]),
    listar: vi.fn().mockResolvedValue({ itens: [importacao], total: 1 }),
    enviar: vi.fn().mockResolvedValue(importacao),
    consultar: vi.fn().mockResolvedValue(importacao),
    definirColunas: vi.fn().mockResolvedValue(importacao),
    responderPendencias: vi.fn().mockResolvedValue(importacao),
    confirmar: vi.fn().mockResolvedValue(importacao),
    cancelar: vi.fn().mockResolvedValue(importacao),
    desfazer: vi.fn().mockResolvedValue(importacao),
    registros: vi.fn().mockResolvedValue({ itens: [], total: 0 }),
  }
}
