import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'

import { ContextoDasNotificacoes } from '../../application/notificacoes/contexto'
import type { ServicoDeNotificacoes } from '../../application/notificacoes/servico'
import { CAIXA, criarNotificacoesFalsas } from '../../testes/corporativoFalso'
import { Sino } from './Sino'

async function montar(servico: ServicoDeNotificacoes) {
  await act(async () => {
    render(
      <ContextoDasNotificacoes value={servico}>
        <MemoryRouter>
          <Sino />
        </MemoryRouter>
      </ContextoDasNotificacoes>,
    )
  })
  return userEvent.setup()
}

describe('sino de notificações', () => {
  it('mostra quantas são novas e abre a lista', async () => {
    const usuario = await montar(criarNotificacoesFalsas())

    await usuario.click(await screen.findByRole('button', { name: 'Notificações, 1 nova' }))

    expect(screen.getByText('O seu pedido foi resolvido, segundo Compesa.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Andamento: Compesa/ })).toHaveAttribute(
      'href',
      '/cidade/meus-pedidos',
    )
  })

  it('marca a notificação como lida ao abrir', async () => {
    const servico = criarNotificacoesFalsas()
    const usuario = await montar(servico)

    await usuario.click(await screen.findByRole('button', { name: /Notificações/ }))
    await usuario.click(screen.getByRole('link', { name: /Andamento: Compesa/ }))

    expect(servico.marcarComoLida).toHaveBeenCalledWith(CAIXA.itens[0]?.id)
  })

  it('marca todas de uma vez', async () => {
    const servico = criarNotificacoesFalsas()
    const usuario = await montar(servico)

    await usuario.click(await screen.findByRole('button', { name: /Notificações/ }))
    await usuario.click(screen.getByRole('button', { name: 'Marcar todas como lidas' }))

    expect(servico.marcarTodasComoLidas).toHaveBeenCalled()
  })

  it('avisa quando não consegue atualizar', async () => {
    const servico = criarNotificacoesFalsas({
      caixa: () => Promise.reject(new Error('fora do ar')),
    })
    const usuario = await montar(servico)

    await usuario.click(await screen.findByRole('button', { name: /Notificações/ }))

    expect(screen.getByText(/Não foi possível atualizar agora/)).toBeInTheDocument()
  })
})
