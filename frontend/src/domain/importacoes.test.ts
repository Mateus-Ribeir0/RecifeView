import { describe, expect, it } from 'vitest'

import { descreverDecisoes, descreverFonte, type DecisoesDaImportacao } from './importacoes'

const SEM_DECISOES: DecisoesDaImportacao = {
  fonte: null,
  dataDoRetrato: null,
  mapeamento: {},
  valoresFixos: {},
  formatoDeData: null,
  substituicoes: {},
  padraoParaValores: {},
  datasInvalidas: null,
  repetidosNaBase: null,
  repetidosNoArquivo: null,
}

describe('descreverFonte', () => {
  it('diz a fonte quando ela já é conhecida', () => {
    expect(descreverFonte({ fonte: 'OUVIDORIA', layout: 'manual' })).toBe('Ouvidoria')
  })

  it('não chama de várias fontes um arquivo que ainda não teve a fonte escolhida', () => {
    expect(descreverFonte({ fonte: null, layout: 'manual' })).toBe('fonte a definir')
  })

  it('reconhece o dataset do grupo como várias fontes', () => {
    expect(descreverFonte({ fonte: null, layout: 'dataset' })).toBe('várias fontes')
  })
})

describe('descreverDecisoes', () => {
  it('traduz as escolhas para o texto da tela', () => {
    const decisoes = {
      ...SEM_DECISOES,
      formatoDeData: 'dia_mes_ano',
      repetidosNoArquivo: 'manter_todos',
    }

    expect(descreverDecisoes(decisoes)).toEqual([
      'Repetidos no arquivo: manter todos',
      'Ordem das datas: dia/mês/ano',
    ])
  })

  it('conta os valores decididos com o plural certo', () => {
    const decisoes = {
      ...SEM_DECISOES,
      substituicoes: { bairro: { X: 'Y' }, situacao: { A: 'B', C: 'D' }, orgao: {} },
    }

    expect(descreverDecisoes(decisoes)).toEqual([
      'Bairro: 1 valor decidido',
      'Situação: 2 valores decididos',
    ])
  })
})
