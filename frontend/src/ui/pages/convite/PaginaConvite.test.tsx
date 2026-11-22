import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it } from 'vitest'

import { ProvedorDeSessao } from '../../../application/autenticacao/ProvedorDeSessao'
import type { ServicoDeAutenticacao } from '../../../application/autenticacao/servico'
import { ErroDoRecifeView } from '../../../domain/erros'
import { criarServicoFalso } from '../../../testes/servicoFalso'
import { PaginaConvite } from './PaginaConvite'

const SENHA = 'Compesa@Recife2026'

async function montar(servico: ServicoDeAutenticacao) {
  const roteador = createMemoryRouter(
    [
      { path: '/convite/:token', element: <PaginaConvite /> },
      { path: '/corporativo', element: <h1>Área corporativa aberta</h1> },
    ],
    { initialEntries: ['/convite/token-do-convite'] },
  )
  await act(async () => {
    render(
      <ProvedorDeSessao servico={servico}>
        <RouterProvider router={roteador} />
      </ProvedorDeSessao>,
    )
  })
  return userEvent.setup()
}

describe('convite da área corporativa', () => {
  it('mostra para quem é e o órgão antes de definir a senha', async () => {
    await montar(criarServicoFalso())

    expect(await screen.findByRole('heading', { name: 'Defina a sua senha' })).toBeInTheDocument()
    expect(screen.getByText('Compesa')).toBeInTheDocument()
  })

  it('define a senha, entra e vai para a área corporativa', async () => {
    const servico = criarServicoFalso()
    const usuario = await montar(servico)

    await usuario.type(await screen.findByLabelText('Senha'), SENHA)
    await usuario.type(screen.getByLabelText('Confirme a senha'), SENHA)
    await usuario.click(screen.getByRole('button', { name: 'Salvar senha e entrar' }))

    expect(servico.aceitarConvite).toHaveBeenCalledWith({ token: 'token-do-convite', senha: SENHA })
    expect(await screen.findByText('Área corporativa aberta')).toBeInTheDocument()
  })

  it('não manda senha que não confere', async () => {
    const servico = criarServicoFalso()
    const usuario = await montar(servico)

    await usuario.type(await screen.findByLabelText('Senha'), SENHA)
    await usuario.type(screen.getByLabelText('Confirme a senha'), 'outra-senha-qualquer')
    await usuario.click(screen.getByRole('button', { name: 'Salvar senha e entrar' }))

    expect(servico.aceitarConvite).not.toHaveBeenCalled()
  })

  it('convite vencido explica o que fazer', async () => {
    const erro = new ErroDoRecifeView(
      'convite_invalido',
      'Este convite venceu, já foi usado ou foi trocado por um mais novo.',
    )
    await montar(criarServicoFalso({ abrirConvite: () => Promise.reject(erro) }))

    expect(
      await screen.findByRole('heading', { name: 'Este convite não vale mais' }),
    ).toBeInTheDocument()
  })
})
