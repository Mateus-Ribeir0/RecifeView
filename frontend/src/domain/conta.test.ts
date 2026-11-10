import { describe, expect, it } from 'vitest'

import {
  avaliarSenhaDoCadastro,
  codigoCompleto,
  errosDoCadastro,
  mascararCodigo,
  mascararNome,
  normalizarEmail,
  sugerirEmail,
  validarNome,
} from './conta'

describe('e-mail', () => {
  it('normaliza espaço e maiúscula', () => {
    expect(normalizarEmail('  Maria@Exemplo.COM ')).toBe('maria@exemplo.com')
  })

  it('sugere o domínio certo quando a pessoa digita errado', () => {
    expect(sugerirEmail('maria@gmial.com')).toBe('maria@gmail.com')
    expect(sugerirEmail('maria@hotmal.com')).toBe('maria@hotmail.com')
    expect(sugerirEmail('maria@gmail.com')).toBeNull()
    expect(sugerirEmail('maria@empresa.com.br')).toBeNull()
    expect(sugerirEmail('sem-arroba')).toBeNull()
  })
})

describe('nome', () => {
  it('tira número e símbolo enquanto a pessoa digita', () => {
    expect(mascararNome('Maria 123 <b>  Silva')).toBe('Maria b Silva')
    expect(mascararNome("João D'Ávila-Souza")).toBe("João D'Ávila-Souza")
  })

  it('recusa nome curto ou mal formado', () => {
    expect(validarNome('A')).toBeTruthy()
    expect(validarNome('Ana --')).toBeTruthy()
    expect(validarNome('Ana Clara')).toBeNull()
  })
})

describe('código', () => {
  it('aceita só seis dígitos e separa em dois grupos', () => {
    expect(mascararCodigo('12a3456789')).toBe('123 456')
    expect(mascararCodigo('12')).toBe('12')
    expect(codigoCompleto('123 456')).toBe(true)
    expect(codigoCompleto('123 45')).toBe(false)
  })
})

describe('cadastro', () => {
  const valido = {
    nome: 'Maria da Silva',
    email: 'maria@exemplo.com',
    senha: 'uma senha bem comprida',
    confirmacao: 'uma senha bem comprida',
    aceitouOsTermos: true,
  }

  it('não aponta erro quando está tudo certo', () => {
    expect(errosDoCadastro(valido)).toEqual({})
  })

  it('aponta cada campo que falta', () => {
    const erros = errosDoCadastro({
      ...valido,
      nome: '',
      email: 'x',
      confirmacao: 'outra',
      aceitouOsTermos: false,
    })
    expect(Object.keys(erros).sort()).toEqual(['confirmacao', 'email', 'nome', 'termos'])
  })

  it('não deixa a senha conter o começo do e-mail', () => {
    const requisitos = avaliarSenhaDoCadastro({
      senha: 'maria-e-uma-senha',
      confirmacao: 'maria-e-uma-senha',
      email: 'maria@exemplo.com',
    })
    expect(requisitos.map((requisito) => requisito.atendido)).toEqual([true, false, true])
  })
})
