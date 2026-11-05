import { describe, expect, it, vi } from 'vitest'

import { CacheDeConsultas } from './cache'

function aguardar() {
  return new Promise((resolver) => setTimeout(resolver))
}

describe('cache de consultas', () => {
  it('guarda a resposta e não busca de novo', async () => {
    const cache = new CacheDeConsultas()
    const buscar = vi.fn().mockResolvedValue(10)

    cache.garantir('grupo', 'a', buscar)
    await aguardar()
    cache.garantir('grupo', 'a', buscar)

    expect(buscar).toHaveBeenCalledTimes(1)
    expect(cache.ler('a')).toEqual({ situacao: 'pronta', dados: 10 })
  })

  it('avisa quem assina quando a resposta chega', async () => {
    const cache = new CacheDeConsultas()
    const ouvinte = vi.fn()
    cache.assinar(ouvinte)

    cache.garantir('grupo', 'a', () => Promise.resolve(1))
    await aguardar()

    expect(ouvinte).toHaveBeenCalledTimes(2)
  })

  it('registra o erro para a tela poder tentar de novo', async () => {
    const cache = new CacheDeConsultas()
    const falha = new Error('fora do ar')

    cache.garantir('grupo', 'a', () => Promise.reject(falha))
    await aguardar()

    expect(cache.ler('a')).toEqual({ situacao: 'erro', erro: falha })
  })

  it('lembra a última resposta do grupo enquanto a próxima chega', async () => {
    const cache = new CacheDeConsultas()
    cache.garantir('grupo', 'a', () => Promise.resolve('antiga'))
    await aguardar()

    cache.garantir('grupo', 'b', () => new Promise(() => undefined))

    expect(cache.ler('b')).toEqual({ situacao: 'carregando' })
    expect(cache.ultimaPronta('grupo')).toBe('antiga')
  })

  it('esquece tudo depois de uma importação', async () => {
    const cache = new CacheDeConsultas()
    cache.garantir('grupo', 'a', () => Promise.resolve(1))
    await aguardar()

    cache.esquecerTudo()

    expect(cache.ler('a')).toBeUndefined()
    expect(cache.ultimaPronta('grupo')).toBeUndefined()
  })
})
