import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../../application/autenticacao/ProvedorDeSessao'
import type { ServicoDeAutenticacao } from '../../../application/autenticacao/servico'
import { ContextoDasContribuicoes } from '../../../application/contribuicoes/contexto'
import { criarContribuicoesFalsas } from '../../../testes/contribuicaoFalsa'
import { ErroDoRecifeView } from '../../../domain/erros'
import { criarServicoFalso } from '../../../testes/servicoFalso'
import { SoParaVisitantes } from '../../app/SoParaVisitantes'
import { PaginaCadastrar } from './PaginaCadastrar'

const SENHA = 'uma senha bem comprida'

function montar(servico: ServicoDeAutenticacao) {
  render(
    <MemoryRouter initialEntries={['/cadastrar']}>
      <ProvedorDeSessao servico={servico}>
        <ContextoDasContribuicoes value={criarContribuicoesFalsas()}>
          <Routes>
            <Route element={<SoParaVisitantes />}>
              <Route path="/cadastrar" element={<PaginaCadastrar />} />
            </Route>
            <Route path="/cidade" element={<h1>Área do cidadão</h1>} />
          </Routes>
        </ContextoDasContribuicoes>
      </ProvedorDeSessao>
    </MemoryRouter>,
  )
  return userEvent.setup()
}

async function preencher(usuario: ReturnType<typeof userEvent.setup>, email: string) {
  await usuario.type(await screen.findByLabelText('Nome'), 'Maria da Silva')
  await usuario.type(screen.getByLabelText('E-mail'), email)
  await usuario.type(screen.getByLabelText('Senha'), SENHA)
  await usuario.type(screen.getByLabelText('Repita a senha'), SENHA)
  await usuario.click(screen.getByRole('checkbox'))
}

describe('cadastro de cidadão', () => {
  it('sugere o domínio certo e corrige com um clique', async () => {
    const usuario = montar(criarServicoFalso())

    await usuario.type(await screen.findByLabelText('E-mail'), 'maria@gmial.com')
    await usuario.click(await screen.findByRole('button', { name: 'Usar este' }))

    expect(screen.getByLabelText('E-mail')).toHaveValue('maria@gmail.com')
  })

  it('não envia sem aceitar os termos', async () => {
    const criarConta = vi.fn()
    const usuario = montar(criarServicoFalso({ criarConta }))

    await usuario.type(await screen.findByLabelText('Nome'), 'Maria da Silva')
    await usuario.click(screen.getByRole('button', { name: 'Criar conta e entrar' }))

    expect(await screen.findByText(/aceite como usamos os seus dados/)).toBeInTheDocument()
    expect(criarConta).not.toHaveBeenCalled()
  })

  it('cria a conta e já entra na área do cidadão', async () => {
    const usuario = montar(criarServicoFalso())

    await preencher(usuario, ' Maria@Exemplo.com ')
    await usuario.click(screen.getByRole('button', { name: 'Criar conta e entrar' }))

    expect(await screen.findByRole('heading', { name: 'Área do cidadão' })).toBeInTheDocument()
  })

  it('envia o e-mail normalizado e mostra no campo quando ele já tem conta', async () => {
    const recusa = new ErroDoRecifeView(
      'cadastro_invalido',
      'Este e-mail já tem conta.',
      null,
      'email',
    )
    const criarConta = vi.fn().mockRejectedValue(recusa)
    const usuario = montar(criarServicoFalso({ criarConta }))

    await preencher(usuario, ' Maria@Exemplo.com ')
    await usuario.click(screen.getByRole('button', { name: 'Criar conta e entrar' }))

    expect(criarConta).toHaveBeenCalledWith(
      expect.objectContaining({ email: 'maria@exemplo.com', aceitouOsTermos: true, site: '' }),
    )
    expect(await screen.findByText('Este e-mail já tem conta.')).toBeInTheDocument()
  })
})
