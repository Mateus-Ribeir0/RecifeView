import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../../application/autenticacao/ProvedorDeSessao'
import type { ServicoDeAutenticacao } from '../../../application/autenticacao/servico'
import { ContextoDasContribuicoes } from '../../../application/contribuicoes/contexto'
import { criarContribuicoesFalsas } from '../../../testes/contribuicaoFalsa'
import { criarServicoFalso } from '../../../testes/servicoFalso'
import { PaginaCadastrar } from './PaginaCadastrar'

const SENHA = 'uma senha bem comprida'

function montar(servico: ServicoDeAutenticacao) {
  render(
    <MemoryRouter>
      <ProvedorDeSessao servico={servico}>
        <ContextoDasContribuicoes value={criarContribuicoesFalsas()}>
          <PaginaCadastrar />
        </ContextoDasContribuicoes>
      </ProvedorDeSessao>
    </MemoryRouter>,
  )
  return userEvent.setup()
}

async function preencher(usuario: ReturnType<typeof userEvent.setup>, email: string) {
  await usuario.type(screen.getByLabelText('Nome'), 'Maria da Silva')
  await usuario.type(screen.getByLabelText('E-mail'), email)
  await usuario.type(screen.getByLabelText('Senha'), SENHA)
  await usuario.type(screen.getByLabelText('Repita a senha'), SENHA)
  await usuario.click(screen.getByRole('checkbox'))
}

describe('cadastro de cidadão', () => {
  it('sugere o domínio certo e corrige com um clique', async () => {
    const usuario = montar(criarServicoFalso())

    await usuario.type(screen.getByLabelText('E-mail'), 'maria@gmial.com')
    await usuario.click(await screen.findByRole('button', { name: 'Usar este' }))

    expect(screen.getByLabelText('E-mail')).toHaveValue('maria@gmail.com')
  })

  it('não envia sem aceitar os termos', async () => {
    const criarConta = vi.fn()
    const usuario = montar(criarServicoFalso({ criarConta }))

    await usuario.type(screen.getByLabelText('Nome'), 'Maria da Silva')
    await usuario.click(screen.getByRole('button', { name: 'Criar conta e receber o código' }))

    expect(await screen.findByText(/aceite como usamos os seus dados/)).toBeInTheDocument()
    expect(criarConta).not.toHaveBeenCalled()
  })

  it('cria a conta, pede o código e confirma com a mesma senha', async () => {
    const criarConta = vi.fn().mockResolvedValue('Enviamos um código.')
    const confirmarEmail = vi.fn().mockResolvedValue(undefined)
    const usuario = montar(criarServicoFalso({ criarConta, confirmarEmail }))

    await preencher(usuario, ' Maria@Exemplo.com ')
    await usuario.click(screen.getByRole('button', { name: 'Criar conta e receber o código' }))

    expect(criarConta).toHaveBeenCalledWith(
      expect.objectContaining({ email: 'maria@exemplo.com', aceitouOsTermos: true, site: '' }),
    )
    const codigo = await screen.findByLabelText('Código de 6 dígitos')
    await usuario.type(codigo, '123456')
    expect(codigo).toHaveValue('123 456')
    await usuario.click(screen.getByRole('button', { name: 'Confirmar e entrar' }))

    expect(confirmarEmail).toHaveBeenCalledWith({
      email: 'maria@exemplo.com',
      codigo: '123456',
      senha: SENHA,
    })
  })
})
