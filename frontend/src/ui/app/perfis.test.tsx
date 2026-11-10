import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../application/autenticacao/ProvedorDeSessao'
import type { ServicoDeAutenticacao } from '../../application/autenticacao/servico'
import { CIDADA, criarServicoFalso, GESTORA } from '../../testes/servicoFalso'
import { PaginaEntrar } from '../pages/entrar/PaginaEntrar'
import { RotaProtegida } from './RotaProtegida'
import { SoParaCidadaos } from './SoParaCidadaos'
import { SoParaGestao } from './SoParaGestao'
import { SoParaVisitantes } from './SoParaVisitantes'

function montar(servico: ServicoDeAutenticacao, rotaInicial: string) {
  const roteador = createMemoryRouter(
    [
      {
        element: <SoParaVisitantes />,
        children: [
          { path: '/entrar', element: <PaginaEntrar area="cidade" /> },
          { path: '/entrar/gestao', element: <PaginaEntrar area="gestao" /> },
        ],
      },
      {
        element: <RotaProtegida />,
        children: [
          {
            path: '/cidade',
            element: <SoParaCidadaos />,
            children: [{ index: true, element: <h1>Área do cidadão</h1> }],
          },
          {
            path: '/painel',
            element: <SoParaGestao />,
            children: [{ index: true, element: <h1>Painel da gestão</h1> }],
          },
        ],
      },
    ],
    { initialEntries: [rotaInicial] },
  )
  render(
    <ProvedorDeSessao servico={servico}>
      <RouterProvider router={roteador} />
    </ProvedorDeSessao>,
  )
}

async function entrar() {
  await userEvent.type(await screen.findByLabelText('E-mail'), 'maria@exemplo.com')
  await userEvent.type(screen.getByLabelText('Senha'), 'uma senha bem comprida')
  await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
}

describe('áreas por perfil', () => {
  it('cidadão que tenta abrir o painel vai para a área do cidadão', async () => {
    montar(criarServicoFalso({ restaurarSessao: vi.fn().mockResolvedValue(CIDADA) }), '/painel')

    expect(await screen.findByRole('heading', { name: 'Área do cidadão' })).toBeInTheDocument()
  })

  it('gestão que tenta abrir a área do cidadão vai para o painel', async () => {
    montar(criarServicoFalso({ restaurarSessao: vi.fn().mockResolvedValue(GESTORA) }), '/cidade')

    expect(await screen.findByRole('heading', { name: 'Painel da gestão' })).toBeInTheDocument()
  })

  it('gestão abre o painel', async () => {
    montar(criarServicoFalso({ restaurarSessao: vi.fn().mockResolvedValue(GESTORA) }), '/painel')

    expect(await screen.findByRole('heading', { name: 'Painel da gestão' })).toBeInTheDocument()
  })

  it('cidadão entra e cai na área do cidadão', async () => {
    const entrarNoServico = vi.fn().mockResolvedValue(CIDADA)
    montar(criarServicoFalso({ entrar: entrarNoServico }), '/entrar')

    await entrar()

    expect(await screen.findByRole('heading', { name: 'Área do cidadão' })).toBeInTheDocument()
    expect(entrarNoServico).toHaveBeenCalledWith(expect.objectContaining({ area: 'cidade' }))
  })

  it('a porta da gestão avisa a API de qual área é o login', async () => {
    const entrarNoServico = vi.fn().mockResolvedValue(GESTORA)
    montar(criarServicoFalso({ entrar: entrarNoServico }), '/entrar/gestao')

    expect(await screen.findByRole('heading', { name: 'Entrar na área da gestão' })).toBeVisible()
    await entrar()

    expect(entrarNoServico).toHaveBeenCalledWith(expect.objectContaining({ area: 'gestao' }))
    expect(await screen.findByRole('heading', { name: 'Painel da gestão' })).toBeInTheDocument()
  })
})
