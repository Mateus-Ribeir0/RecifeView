import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ContextoDasContribuicoes } from '../../../application/contribuicoes/contexto'
import { ContextoDoOrgao } from '../../../application/corporativo/contexto'
import type { ServicoDoOrgao } from '../../../application/corporativo/servico'
import { criarContribuicoesFalsas } from '../../../testes/contribuicaoFalsa'
import { criarOrgaoFalso, OCORRENCIA_DO_ORGAO } from '../../../testes/corporativoFalso'
import { PaginaOcorrenciaDoOrgao } from './PaginaOcorrenciaDoOrgao'
import { PaginaOcorrenciasDoOrgao } from './PaginaOcorrenciasDoOrgao'

vi.mock('../../map/MapaDeEscolhaDoBairro', () => ({ MapaDeEscolhaDoBairro: () => null }))

function comProvedores(servico: ServicoDoOrgao, filho: ReactNode) {
  return (
    <ContextoDasContribuicoes value={criarContribuicoesFalsas()}>
      <ContextoDoOrgao value={servico}>{filho}</ContextoDoOrgao>
    </ContextoDasContribuicoes>
  )
}

async function montar(servico: ServicoDoOrgao, caminho: string) {
  const roteador = createMemoryRouter(
    [
      { path: '/corporativo/ocorrencias', element: <PaginaOcorrenciasDoOrgao /> },
      { path: '/corporativo/ocorrencias/:id', element: <PaginaOcorrenciaDoOrgao /> },
    ],
    { initialEntries: [caminho] },
  )
  await act(async () => {
    render(comProvedores(servico, <RouterProvider router={roteador} />))
  })
  return userEvent.setup()
}

describe('área corporativa', () => {
  it('a fila mostra a ocorrência com o mesmo problema e quem acompanha', async () => {
    const servico = criarOrgaoFalso()
    await montar(servico, '/corporativo/ocorrencias?aba=novas')

    expect(await screen.findByText('ENC-2026-000007')).toBeInTheDocument()
    expect(screen.getByText(/Mesmo problema: 1 outra ocorrência/)).toBeInTheDocument()
    expect(screen.getByText('2 pessoas acompanham')).toBeInTheDocument()
    expect(servico.fila).toHaveBeenCalledWith(
      expect.objectContaining({ aba: 'novas', deslocamento: 0 }),
    )
  })

  it('trocar de aba muda o filtro da fila', async () => {
    const servico = criarOrgaoFalso()
    const usuario = await montar(servico, '/corporativo/ocorrencias')

    await usuario.click(await screen.findByRole('button', { name: /Resolvidas/ }))

    expect(servico.fila).toHaveBeenLastCalledWith(expect.objectContaining({ aba: 'resolvidas' }))
  })

  it('resolver exige a resposta ao cidadão', async () => {
    const servico = criarOrgaoFalso()
    const usuario = await montar(servico, '/corporativo/ocorrencias/7')

    await usuario.click(await screen.findByRole('radio', { name: /Resolvida/ }))
    await usuario.click(screen.getByRole('button', { name: /Enviar para 2 ocorrências/ }))

    expect(screen.getByText('Escreva a resposta para quem fez o pedido.')).toBeInTheDocument()
    expect(servico.responder).not.toHaveBeenCalled()
  })

  it('responde junto ao mesmo problema e avisa o que foi registrado', async () => {
    const servico = criarOrgaoFalso()
    const usuario = await montar(servico, '/corporativo/ocorrencias/7')

    await usuario.click(await screen.findByRole('radio', { name: /Resolvida/ }))
    await usuario.type(screen.getByLabelText('Conte o que foi feito'), 'Galeria desobstruída')
    await usuario.click(screen.getByRole('button', { name: /Enviar para 2 ocorrências/ }))

    expect(servico.responder).toHaveBeenCalledWith(
      OCORRENCIA_DO_ORGAO.id,
      expect.objectContaining({
        situacao: 'resolvido',
        respostaAoCidadao: 'Galeria desobstruída',
        tambem: [8],
      }),
    )
    expect(await screen.findByText('Resposta registrada')).toBeInTheDocument()
  })

  it('a ocorrência de outro órgão com o mesmo problema não abre', async () => {
    await montar(criarOrgaoFalso(), '/corporativo/ocorrencias/7')

    expect(await screen.findByRole('link', { name: 'ENC-2026-000008' })).toBeInTheDocument()
    expect(screen.getByText('Emlurb')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Emlurb' })).not.toBeInTheDocument()
  })
})
