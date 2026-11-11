import { describe, expect, it } from 'vitest'

import { normalizarProtocolo, protocoloEValido } from './pedidos'

describe('protocolo', () => {
  it('tira os espaços e passa para maiúsculas, como a API', () => {
    expect(normalizarProtocolo(' 2026 / ab-1 ')).toBe('2026/AB-1')
  })

  it('aceita letras, números, ponto, barra e hífen', () => {
    expect(protocoloEValido('2026.0001/OUV-1')).toBe(true)
  })

  it('recusa o que não parece protocolo', () => {
    expect(protocoloEValido('12')).toBe(false)
    expect(protocoloEValido('Rua do Sol, 10')).toBe(false)
  })
})
