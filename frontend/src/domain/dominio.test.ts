import { describe, expect, it } from 'vitest'

import { pareceEmail } from './acesso'
import { formatarNumero } from './formatacao'
import { avaliarNovaSenha, novaSenhaEstaValida } from './senha'
import { iniciaisDoNome } from './usuario'

const BASE = {
  senhaAtual: 'senha-temporaria',
  email: 'gestora@recife.pe.gov.br',
}

describe('nova senha', () => {
  it('aceita uma senha longa, nova, sem o e-mail e confirmada', () => {
    const dados = {
      ...BASE,
      novaSenha: 'ponte-boa-vista-1840',
      confirmacao: 'ponte-boa-vista-1840',
    }
    expect(novaSenhaEstaValida(dados)).toBe(true)
  })

  it('aponta cada requisito que falta', () => {
    const dados = { ...BASE, novaSenha: 'gestora-1', confirmacao: 'outra' }
    const pendentes = avaliarNovaSenha(dados)
      .filter((requisito) => !requisito.atendido)
      .map((requisito) => requisito.descricao)
    expect(pendentes).toEqual([
      'Pelo menos 12 caracteres',
      'Sem a parte do seu e-mail antes do @',
      'As duas senhas conferem',
    ])
  })

  it('recusa repetir a senha atual', () => {
    const dados = { ...BASE, novaSenha: BASE.senhaAtual, confirmacao: BASE.senhaAtual }
    expect(novaSenhaEstaValida(dados)).toBe(false)
  })
})

describe('apoio ao domínio', () => {
  it('forma as iniciais sem preposições', () => {
    expect(iniciaisDoNome('Gestora de Demonstração')).toBe('GD')
    expect(iniciaisDoNome('Ana')).toBe('A')
  })

  it('formata números no padrão brasileiro', () => {
    expect(formatarNumero(2643481)).toBe('2.643.481')
  })

  it('reconhece um e-mail plausível', () => {
    expect(pareceEmail(' gestora@recife.pe.gov.br ')).toBe(true)
    expect(pareceEmail('gestora@recife')).toBe(false)
  })
})
