import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../../application/autenticacao/ProvedorDeSessao'
import { ContextoDaInformacao } from '../../../application/informacao/contexto'
import type { ServicoDeInformacao } from '../../../application/informacao/servico'
import { criarInformacaoFalsa, PEDIDO } from '../../../testes/informacaoFalsa'
import { CIDADA, criarServicoFalso } from '../../../testes/servicoFalso'
import { PaginaMeusPedidos } from './PaginaMeusPedidos'

function montar(servico: ServicoDeInformacao, recebeAvisos = true) {
  const sessao = criarServicoFalso({
    restaurarSessao: vi.fn().mockResolvedValue({ ...CIDADA, recebeAvisos }),
  })
  render(
    <MemoryRouter>
      <ProvedorDeSessao servico={sessao}>
        <ContextoDaInformacao value={servico}>
          <PaginaMeusPedidos />
        </ContextoDaInformacao>
      </ProvedorDeSessao>
    </MemoryRouter>,
  )
  return userEvent.setup()
}

describe('meus pedidos', () => {
  it('lista os protocolos guardados com o andamento', async () => {
    montar(criarInformacaoFalsa())

    expect(await screen.findByText(/Protocolo TESTE-0001, guardado em/)).toBeInTheDocument()
    expect(screen.getByText('Neoenergia Pernambuco')).toBeInTheDocument()
  })

  it('guarda um protocolo novo e recarrega a lista', async () => {
    const meusPedidos = vi.fn().mockResolvedValue([])
    const servico = criarInformacaoFalsa({ meusPedidos })
    const usuario = montar(servico)

    await usuario.type(await screen.findByLabelText('Protocolo do pedido'), 'TESTE-0002')
    await usuario.click(screen.getByRole('button', { name: 'Acompanhar' }))

    expect(servico.acompanharPedido).toHaveBeenCalledWith('TESTE-0002')
    expect(meusPedidos).toHaveBeenCalledTimes(2)
  })

  it('diz quando os avisos por e-mail estão desligados', async () => {
    montar(criarInformacaoFalsa(), false)

    expect(await screen.findByText(/Os avisos por e-mail estão desligados/)).toBeInTheDocument()
  })

  it('tira um protocolo da lista', async () => {
    const servico = criarInformacaoFalsa()
    const usuario = montar(servico)

    await usuario.click(await screen.findByRole('button', { name: 'Deixar de acompanhar' }))

    expect(servico.deixarDeAcompanhar).toHaveBeenCalledWith(PEDIDO.id)
  })
})
