import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ContextoDasContribuicoes } from '../../../application/contribuicoes/contexto'
import type { ServicoDeContribuicoes } from '../../../application/contribuicoes/servico'
import { criarContribuicoesFalsas, RESUMO } from '../../../testes/contribuicaoFalsa'
import { PaginaContribuicoes } from './PaginaContribuicoes'

function montar(servico: ServicoDeContribuicoes) {
  const roteador = createMemoryRouter(
    [
      { path: '/painel/contribuicoes', element: <PaginaContribuicoes /> },
      { path: '/painel/importacoes/:id', element: <h1>Importação aberta</h1> },
    ],
    { initialEntries: ['/painel/contribuicoes'] },
  )
  render(
    <ContextoDasContribuicoes value={servico}>
      <RouterProvider router={roteador} />
    </ContextoDasContribuicoes>,
  )
  return userEvent.setup()
}

describe('tela de contribuições', () => {
  it('trava o pacote enquanto houver dupla sem decisão', async () => {
    montar(criarContribuicoesFalsas())

    const botao = await screen.findByRole('button', { name: 'Gerar pacote para importação' })

    expect(botao).toBeDisabled()
    expect(screen.getByText('Decida 1 dupla no pente fino para gerar o pacote.')).toBeVisible()
  })

  it('registra a decisão da gestão e atualiza a fila', async () => {
    const decidir = vi.fn().mockResolvedValue(undefined)
    const resumo = vi.fn().mockResolvedValue(RESUMO)
    const usuario = montar(criarContribuicoesFalsas({ decidir, resumo }))

    await usuario.click(await screen.findByRole('button', { name: 'É a mesma ocorrência' }))

    expect(decidir).toHaveBeenCalledWith(9, 'mesma')
    expect(resumo).toHaveBeenCalledTimes(2)
  })

  it('mostra por que a dupla foi apontada', async () => {
    montar(criarContribuicoesFalsas())

    expect(await screen.findByText('Números próximos')).toBeInTheDocument()
    expect(screen.getByText('Semelhança 84%')).toBeInTheDocument()
  })

  it('leva à importação depois de gerar o pacote', async () => {
    const usuario = montar(
      criarContribuicoesFalsas({
        resumo: vi.fn().mockResolvedValue({ ...RESUMO, aguardandoRevisao: 0 }),
        pares: vi.fn().mockResolvedValue([]),
      }),
    )

    await usuario.click(await screen.findByRole('button', { name: 'Gerar pacote para importação' }))

    expect(await screen.findByRole('heading', { name: 'Importação aberta' })).toBeInTheDocument()
  })
})
