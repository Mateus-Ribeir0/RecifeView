import { describe, expect, it } from 'vitest'

import {
  RASCUNHO_VAZIO,
  chaveDoNome,
  descreverEndereco,
  errosDoPasso,
  gerarChaveDeEnvio,
  passoDoCampo,
  podeGerarPacote,
  type ResumoDasContribuicoes,
} from './contribuicoes'

const RESUMO: ResumoDasContribuicoes = {
  relatos: 3,
  ocorrencias: 2,
  somados: 1,
  aguardandoRevisao: 0,
  prontasParaPacote: 2,
  emPacote: 0,
  naBase: 0,
  retiradas: 0,
  semRetorno: 1,
}

describe('passos do relato', () => {
  it('exige o serviço no primeiro passo', () => {
    expect(errosDoPasso('servico', RASCUNHO_VAZIO).servico).toBeTruthy()
    expect(errosDoPasso('servico', { ...RASCUNHO_VAZIO, servicoCodigo: '131' })).toEqual({})
  })

  it('exige bairro e rua, mas não o número', () => {
    const erros = errosDoPasso('local', RASCUNHO_VAZIO)
    expect(Object.keys(erros).sort()).toEqual(['bairro', 'logradouro'])
    const preenchido = { ...RASCUNHO_VAZIO, bairroOficial: 'AFOGADOS', logradouro: 'Rua A1' }
    expect(errosDoPasso('local', preenchido)).toEqual({})
  })

  it('só envia depois de confirmar que leu o aviso', () => {
    expect(errosDoPasso('envio', RASCUNHO_VAZIO).ciente).toBeTruthy()
    expect(errosDoPasso('envio', { ...RASCUNHO_VAZIO, ciente: true })).toEqual({})
  })

  it('leva o erro do servidor de volta ao passo do campo', () => {
    expect(passoDoCampo('detalhe')).toBe('envio')
    expect(passoDoCampo('logradouro')).toBe('local')
    expect(passoDoCampo(null)).toBeNull()
  })
})

describe('chave de envio', () => {
  it('gera uma chave diferente a cada formulário', () => {
    const chave = gerarChaveDeEnvio()
    expect(chave).toMatch(/^[0-9a-f]{32}$/)
    expect(gerarChaveDeEnvio()).not.toBe(chave)
  })
})

describe('pacote', () => {
  it('não libera com dupla em aberto nem sem ocorrência nova', () => {
    expect(podeGerarPacote(RESUMO)).toBe(true)
    expect(podeGerarPacote({ ...RESUMO, aguardandoRevisao: 1 })).toBe(false)
    expect(podeGerarPacote({ ...RESUMO, prontasParaPacote: 0 })).toBe(false)
  })
})

describe('textos', () => {
  it('avisa quando o endereço já foi apagado', () => {
    expect(descreverEndereco({ logradouro: null, numero: null })).toContain('apagado')
    expect(descreverEndereco({ logradouro: 'RUA A', numero: null })).toBe('RUA A, sem número')
    expect(descreverEndereco({ logradouro: 'RUA A', numero: '10' })).toBe('RUA A, 10')
  })

  it('compara nomes de bairro sem depender de acento', () => {
    expect(chaveDoNome('Água Fria')).toBe('AGUA FRIA')
  })
})
