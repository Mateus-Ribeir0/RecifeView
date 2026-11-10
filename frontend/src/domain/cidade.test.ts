import { describe, expect, it } from 'vitest'

import {
  descreverLocal,
  haQuantoTempo,
  resumirOcorrencias,
  type OcorrenciaDaCidade,
} from './cidade'
import { inicioDoPerfil, podeAbrir } from './usuario'

const OCORRENCIA: OcorrenciaDaCidade = {
  id: 'a',
  dataRelato: '2026-11-07',
  servico: 'Buraco na rua',
  tema: 'Ruas e calçadas',
  bairroOficial: 'AFOGADOS',
  bairro: 'Afogados',
  rpa: '5',
  via: 'RUA DA ESPERANCA',
  faixaDeNumeracao: 'entre 100 e 199',
  relatos: 3,
  semRetorno: 2,
  situacao: 'no_painel',
}

describe('relatos da cidade', () => {
  it('descreve o local só com a faixa de numeração', () => {
    expect(descreverLocal(OCORRENCIA)).toBe('RUA DA ESPERANCA, entre 100 e 199')
    expect(descreverLocal({ ...OCORRENCIA, via: null })).toBe('Afogados, rua não identificada')
  })

  it('conta os dias de forma simples', () => {
    const hoje = new Date('2026-11-10T15:00:00')
    expect(haQuantoTempo('2026-11-10', hoje)).toBe('hoje')
    expect(haQuantoTempo('2026-11-09', hoje)).toBe('ontem')
    expect(haQuantoTempo('2026-11-07', hoje)).toBe('há 3 dias')
  })

  it('soma relatos e conta ocorrências uma vez', () => {
    const resumo = resumirOcorrencias([
      OCORRENCIA,
      { ...OCORRENCIA, id: 'b', situacao: 'recebido' },
    ])
    expect(resumo).toEqual({ relatos: 6, ocorrencias: 2, semRetorno: 4, noPainel: 1 })
  })
})

describe('perfis', () => {
  it('manda cada perfil para a sua área', () => {
    expect(inicioDoPerfil('CIDADAO')).toBe('/cidade')
    expect(inicioDoPerfil('GESTOR')).toBe('/painel')
  })

  it('cidadão não abre o painel, gestão abre tudo', () => {
    expect(podeAbrir('CIDADAO', '/painel/importacoes')).toBe(false)
    expect(podeAbrir('CIDADAO', '/cidade/meu-bairro')).toBe(true)
    expect(podeAbrir('GESTOR', '/cidade')).toBe(true)
  })
})
