import { describe, expect, it } from 'vitest'

import { ENCAMINHAMENTO, PREPARO } from '../testes/encaminhamentoFalso'
import { explicarSugestao, podeReenviar, respostasPossiveis } from './encaminhamentos'

describe('encaminhamentos', () => {
  it('só aceita a resposta seguinte do ciclo', () => {
    expect(respostasPossiveis('enviado')).toEqual(['recebido', 'resolvido', 'devolvido'])
    expect(respostasPossiveis('recebido')).toEqual(['resolvido', 'devolvido'])
    expect(respostasPossiveis('resolvido')).toEqual([])
  })

  it('só oferece reenvio depois de falha do canal', () => {
    expect(podeReenviar(ENCAMINHAMENTO)).toBe(false)
    expect(podeReenviar({ ...ENCAMINHAMENTO, situacao: 'falhou' })).toBe(true)
  })

  it('explica a sugestão com o número da evidência', () => {
    expect(explicarSugestao(PREPARO.sugestao)).toBe(
      'O próprio registro aponta este órgão. Nas 100 indicações da Câmara sobre drenagem, 80,0% citam Emlurb.',
    )
  })

  it('diz quando não há sugestão', () => {
    const sem = { ...PREPARO.sugestao, orgao: null, motivo: 'sem_sugestao' as const }

    expect(explicarSugestao(sem)).toContain('Escolha o órgão')
  })
})
