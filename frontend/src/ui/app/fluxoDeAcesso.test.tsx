import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../application/autenticacao/ProvedorDeSessao'
import type { ServicoDeAutenticacao } from '../../application/autenticacao/servico'
import { ErroDoRecifeView } from '../../domain/erros'
import { criarServicoFalso, GESTORA } from '../../testes/servicoFalso'
import { PaginaDefinirSenha } from '../pages/definir-senha/PaginaDefinirSenha'
import { PaginaEntrar } from '../pages/entrar/PaginaEntrar'
import { RotaProtegida } from './RotaProtegida'
import { SoParaVisitantes } from './SoParaVisitantes'

function montar(servico: ServicoDeAutenticacao, rotaInicial: string) {
  const roteador = createMemoryRouter(
    [
      { element: <SoParaVisitantes />, children: [{ path: '/entrar', element: <PaginaEntrar /> }] },
      {
        element: <RotaProtegida />,
        children: [
          { path: '/painel', element: <h1>Painel</h1> },
          { path: '/definir-senha', element: <PaginaDefinirSenha /> },
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

describe('fluxo de acesso', () => {
  it('manda quem não entrou para a tela de entrada', async () => {
    montar(criarServicoFalso(), '/painel')
    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('valida os campos antes de chamar o serviço', async () => {
    const servico = criarServicoFalso()
    montar(servico, '/entrar')
    await userEvent.click(await screen.findByRole('button', { name: 'Entrar' }))

    expect(screen.getByText('Informe o seu e-mail.')).toBeInTheDocument()
    expect(screen.getByText('Informe a sua senha.')).toBeInTheDocument()
    expect(servico.entrar).not.toHaveBeenCalled()
  })

  it('mostra a mensagem da API quando a senha está errada', async () => {
    const recusa = new ErroDoRecifeView('credenciais_invalidas', 'E-mail ou senha incorretos.')
    const servico = criarServicoFalso({ entrar: vi.fn().mockRejectedValue(recusa) })
    montar(servico, '/entrar')

    await userEvent.type(await screen.findByLabelText('E-mail'), GESTORA.email)
    await userEvent.type(screen.getByLabelText('Senha'), 'errada')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail ou senha incorretos.')
    expect(screen.getByLabelText('Senha')).toHaveValue('')
  })

  it('leva ao painel depois de entrar', async () => {
    montar(criarServicoFalso(), '/painel')
    await userEvent.type(await screen.findByLabelText('E-mail'), GESTORA.email)
    await userEvent.type(screen.getByLabelText('Senha'), 'senha-correta-123')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('heading', { name: 'Painel' })).toBeInTheDocument()
  })

  it('exige a troca da senha temporária antes do painel', async () => {
    const primeiroAcesso = { ...GESTORA, deveTrocarSenha: true }
    const servico = criarServicoFalso({
      restaurarSessao: () => Promise.resolve(primeiroAcesso),
      trocarSenha: vi.fn().mockResolvedValue(GESTORA),
    })
    montar(servico, '/painel')

    expect(await screen.findByRole('heading', { name: 'Defina a sua senha' })).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Senha temporária'), 'temporaria-123')
    await userEvent.type(screen.getByLabelText('Nova senha'), 'ponte-boa-vista-1840')
    await userEvent.type(screen.getByLabelText('Confirme a nova senha'), 'ponte-boa-vista-1840')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar senha e continuar' }))

    expect(servico.trocarSenha).toHaveBeenCalledWith({
      senhaAtual: 'temporaria-123',
      novaSenha: 'ponte-boa-vista-1840',
    })
    expect(await screen.findByRole('heading', { name: 'Painel' })).toBeInTheDocument()
  })
})
