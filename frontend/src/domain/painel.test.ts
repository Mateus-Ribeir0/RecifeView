import { describe, expect, it } from 'vitest'

import { classeDoValor, faixasIguais, faixasPorQuantis } from './classes'
import { FILTROS_PADRAO, estaNoPadrao, resumirRecorte, temTerritorio } from './filtros'
import {
  formatarData,
  formatarDataLonga,
  formatarDias,
  formatarNumero,
  formatarPeriodo,
  formatarPorcentagem,
  formatarTamanho,
  SEM_DADO,
} from './formatacao'
import { nomeDaFonte } from './fontes'
import { estaEmProcessamento, estaEncerrada } from './importacoes'
import { nomeDaCategoria, nomeDoOrgao } from './nomes'
import { chaveDoPar, opcaoDoValor, rotuloDaOpcao, valorDaOpcao } from './prioridade'
import { diasEntre, somarDias } from './warRoom'

describe('formatação', () => {
  it('usa o padrão brasileiro nos números', () => {
    expect(formatarNumero(1377158)).toBe('1.377.158')
    expect(formatarNumero(36.3, 1)).toBe('36,3')
    expect(formatarPorcentagem(21.4)).toBe('21%')
  })

  it('não usa travessão quando falta o dado', () => {
    expect(formatarPorcentagem(null)).toBe(SEM_DADO)
    expect(formatarDias(null)).toBe(SEM_DADO)
    expect(formatarData(null)).toBe(SEM_DADO)
  })

  it('escreve dia no singular', () => {
    expect(formatarDias(1)).toBe('1 dia')
    expect(formatarDias(60)).toBe('60 dias')
  })

  it('escreve o intervalo de anos com "a"', () => {
    expect(formatarPeriodo(2021, 2025)).toBe('2021 a 2025')
    expect(formatarPeriodo(2024, 2024)).toBe('2024')
  })

  it('mostra a data no formato do Brasil', () => {
    expect(formatarData('2026-10-07')).toBe('07/10/2026')
    expect(formatarDataLonga('2026-10-07')).toBe('Quarta-feira, 7 de outubro de 2026')
  })

  it('resume o tamanho do arquivo', () => {
    expect(formatarTamanho(2048)).toBe('2 KB')
    expect(formatarTamanho(1572864)).toBe('1,5 MB')
  })
})

describe('nomes', () => {
  it('devolve os acentos que as fontes tiram', () => {
    expect(nomeDaCategoria('ILUMINACAO PUBLICA')).toBe('Iluminação pública')
    expect(nomeDaCategoria('MANUTENCAO EM LAMPADA APAGADA')).toBe('Manutenção em lâmpada apagada')
  })

  it('mantém as siglas de órgão', () => {
    expect(nomeDoOrgao('SEINFRA/INFRAESTRUTURA')).toBe('SEINFRA')
    expect(nomeDoOrgao('EMLURB')).toBe('EMLURB')
  })

  it('diz quando o nome falta', () => {
    expect(nomeDaCategoria(null)).toBe('não informado')
  })

  it('traduz o código da fonte', () => {
    expect(nomeDaFonte('156_EMLURB')).toBe('Central 156 / Emlurb')
    expect(nomeDaFonte(null)).toBe('várias fontes')
  })
})

describe('filtros', () => {
  it('reconhece o recorte padrão', () => {
    expect(estaNoPadrao(FILTROS_PADRAO)).toBe(true)
    expect(estaNoPadrao({ ...FILTROS_PADRAO, rpas: ['1'] })).toBe(false)
  })

  it('reconhece filtro de território', () => {
    expect(temTerritorio({ ...FILTROS_PADRAO, bairros: ['VARZEA'] })).toBe(true)
  })

  it('resume o recorte em texto legível', () => {
    const filtros = {
      ...FILTROS_PADRAO,
      rpas: ['3'],
      bairros: ['VARZEA'],
      categorias: ['ILUMINACAO PUBLICA'],
    }

    expect(resumirRecorte(filtros, () => 'Várzea')).toBe(
      '2021 a 2025 · RPA 3 · Várzea · Iluminação pública',
    )
  })

  it('encurta listas longas', () => {
    const bairros = ['A', 'B', 'C', 'D', 'E', 'F']

    expect(resumirRecorte({ ...FILTROS_PADRAO, bairros })).toContain('A, B, C, D e mais 2')
  })
})

describe('classes do mapa', () => {
  it('reparte em cinco faixas por quantis', () => {
    const faixas = faixasPorQuantis(Array.from({ length: 100 }, (_, indice) => indice + 1))

    expect(faixas).toHaveLength(5)
    expect(classeDoValor(1, faixas)).toBe(1)
    expect(classeDoValor(100, faixas)).toBe(5)
  })

  it('junta limites repetidos', () => {
    expect(faixasPorQuantis([0, 0, 0, 0, 0, 10]).length).toBeLessThan(5)
  })

  it('sem valor não tem classe', () => {
    expect(classeDoValor(null, faixasIguais(10))).toBeNull()
    expect(classeDoValor(3, [])).toBeNull()
  })

  it('divide o índice em faixas iguais', () => {
    expect(faixasIguais(10)[0]).toEqual({ inicio: 0, fim: 2 })
  })
})

describe('escala de Saaty', () => {
  it('converte a posição do controle no julgamento e de volta', () => {
    expect(valorDaOpcao(3)).toBe(3)
    expect(valorDaOpcao(-3)).toBeCloseTo(1 / 3)
    expect(opcaoDoValor(1 / 3)).toBe(-3)
    expect(opcaoDoValor(2)).toBe(2)
  })

  it('escreve o rótulo do lado que pesa mais', () => {
    expect(rotuloDaOpcao(1, 'Risco', 'Atraso')).toBe('igual importância')
    expect(rotuloDaOpcao(3, 'Risco', 'Atraso')).toBe('Risco 3× mais')
    expect(rotuloDaOpcao(-5, 'Risco', 'Atraso')).toBe('Atraso 5× mais')
  })

  it('monta a chave do par', () => {
    expect(chaveDoPar('risco', 'atraso')).toBe('risco|atraso')
  })
})

describe('datas da War Room', () => {
  it('soma dias atravessando o mês', () => {
    expect(somarDias('2026-01-31', 1)).toBe('2026-02-01')
    expect(somarDias('2026-03-01', -1)).toBe('2026-02-28')
  })

  it('conta os dias entre duas datas', () => {
    expect(diasEntre('2026-01-01', '2026-01-31')).toBe(30)
  })
})

describe('situação da importação', () => {
  it('separa o que está em processamento do que terminou', () => {
    expect(estaEmProcessamento('CARREGANDO')).toBe(true)
    expect(estaEmProcessamento('PRONTA')).toBe(false)
    expect(estaEncerrada('DESFEITA')).toBe(true)
  })
})
