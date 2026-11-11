import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ContextoDoRetornoDoOrgao } from '../../../application/encaminhamentos/contexto'
import type { ServicoDeRetornoDoOrgao } from '../../../application/encaminhamentos/servico'
import { criarRetornoFalso } from '../../../testes/encaminhamentoFalso'
import { PaginaRetornoDoOrgao } from './PaginaRetornoDoOrgao'

async function montar(servico: ServicoDeRetornoDoOrgao) {
  const roteador = createMemoryRouter(
    [{ path: '/retorno/:token', element: <PaginaRetornoDoOrgao /> }],
    { initialEntries: ['/retorno/token-do-link'] },
  )
  await act(async () => {
    render(
      <ContextoDoRetornoDoOrgao value={servico}>
        <RouterProvider router={roteador} />
      </ContextoDoRetornoDoOrgao>,
    )
  })
  return userEvent.setup()
}

describe('retorno do órgão pelo link', () => {
  it('mostra o que chegou ao órgão', async () => {
    await montar(criarRetornoFalso())

    expect(await screen.findByRole('heading', { name: 'ENC-2026-000001' })).toBeInTheDocument()
    expect(screen.getByText('TESTE-0001')).toBeInTheDocument()
    expect(screen.getByText(/Terceira indicação no mesmo ponto/)).toBeInTheDocument()
  })

  it('manda a resposta com o token e encerra o ciclo', async () => {
    const servico = criarRetornoFalso()
    const usuario = await montar(servico)

    await usuario.click(await screen.findByRole('radio', { name: 'Resolvido' }))
    await usuario.type(screen.getByLabelText(/Protocolo no órgão/), 'CMP-55')
    await usuario.click(screen.getByRole('button', { name: 'Enviar a resposta' }))

    expect(servico.responder).toHaveBeenCalledWith('token-do-link', {
      situacao: 'resolvido',
      protocoloDoOrgao: 'CMP-55',
      observacao: '',
    })
    expect(await screen.findByText('Resposta registrada')).toBeInTheDocument()
  })

  it('avisa quando o link venceu', async () => {
    const abrir = vi.fn().mockRejectedValue(new Error('venceu'))
    await montar(criarRetornoFalso({ abrir }))

    expect(await screen.findByText('Não foi possível carregar estes dados')).toBeInTheDocument()
  })
})
