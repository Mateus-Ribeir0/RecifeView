import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ContextoDasContribuicoes } from '../../../../application/contribuicoes/contexto'
import { ContextoDaInformacao } from '../../../../application/informacao/contexto'
import type { ServicoDeInformacao } from '../../../../application/informacao/servico'
import { criarContribuicoesFalsas } from '../../../../testes/contribuicaoFalsa'
import { criarInformacaoFalsa } from '../../../../testes/informacaoFalsa'
import { PaginaAcompanhar } from './PaginaAcompanhar'

function montar(servico: ServicoDeInformacao) {
  render(
    <MemoryRouter>
      <ContextoDasContribuicoes value={criarContribuicoesFalsas()}>
        <ContextoDaInformacao value={servico}>
          <PaginaAcompanhar />
        </ContextoDaInformacao>
      </ContextoDasContribuicoes>
    </MemoryRouter>,
  )
  return userEvent.setup()
}

describe('acompanhar um pedido', () => {
  it('mostra a situação e para qual órgão o pedido foi', async () => {
    const servico = criarInformacaoFalsa()
    const usuario = montar(servico)

    await usuario.type(screen.getByLabelText('Protocolo'), 'teste-0001')
    await usuario.click(screen.getByRole('button', { name: 'Consultar' }))

    expect(servico.consultarPedido).toHaveBeenCalledWith('teste-0001')
    expect(await screen.findByText('Neoenergia Pernambuco')).toBeInTheDocument()
    expect(screen.getByText(/Protocolo no órgão: NEO-77/)).toBeInTheDocument()
  })

  it('explica por que um protocolo pode não aparecer', async () => {
    const usuario = montar(criarInformacaoFalsa({ consultarPedido: vi.fn().mockResolvedValue([]) }))

    await usuario.type(screen.getByLabelText('Protocolo'), 'TESTE-9999')
    await usuario.click(screen.getByRole('button', { name: 'Consultar' }))

    expect(
      await screen.findByText('Nenhum pedido com o protocolo TESTE-9999 na base'),
    ).toBeInTheDocument()
  })

  it('não consulta texto que não é protocolo', async () => {
    const usuario = montar(criarInformacaoFalsa())

    await usuario.type(screen.getByLabelText('Protocolo'), 'Rua do Sol, 10')

    expect(screen.getByRole('button', { name: 'Consultar' })).toBeDisabled()
  })
})
