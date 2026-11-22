import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ContextoDosAcessos } from '../../../application/acessos/contexto'
import type { ServicoDeAcessos } from '../../../application/acessos/servico'
import { ContextoDosEncaminhamentos } from '../../../application/encaminhamentos/contexto'
import { ACESSO, criarAcessosFalsos } from '../../../testes/corporativoFalso'
import { criarEncaminhamentosFalsos } from '../../../testes/encaminhamentoFalso'
import { PaginaAcessosCorporativos } from './PaginaAcessosCorporativos'

async function montar(servico: ServicoDeAcessos) {
  await act(async () => {
    render(
      <MemoryRouter>
        <ContextoDosEncaminhamentos value={criarEncaminhamentosFalsos()}>
          <ContextoDosAcessos value={servico}>
            <PaginaAcessosCorporativos />
          </ContextoDosAcessos>
        </ContextoDosEncaminhamentos>
      </MemoryRouter>,
    )
  })
  return userEvent.setup()
}

describe('acessos corporativos', () => {
  it('a administração cria o acesso e o convite sai para o e-mail', async () => {
    const servico = criarAcessosFalsos()
    const usuario = await montar(servico)

    await usuario.click(await screen.findByRole('button', { name: 'Novo acesso' }))
    await usuario.type(screen.getByLabelText('Nome do responsável'), 'Bruno Lima')
    await usuario.type(screen.getByLabelText('E-mail do responsável'), 'bruno@compesa.exemplo')
    await usuario.selectOptions(screen.getByLabelText('Órgão'), 'COMPESA')
    await usuario.click(screen.getByRole('button', { name: 'Criar e mandar o convite' }))

    expect(servico.criar).toHaveBeenCalledWith({
      nome: 'Bruno Lima',
      email: 'bruno@compesa.exemplo',
      orgao: 'COMPESA',
    })
    expect(
      await screen.findByText(/Convite enviado para bruno@compesa.exemplo/),
    ).toBeInTheDocument()
  })

  it('a lista mostra a situação do convite e permite reenviar', async () => {
    const servico = criarAcessosFalsos()
    const usuario = await montar(servico)

    expect(await screen.findByText('Convite enviado')).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Reenviar convite' }))

    expect(servico.reenviarConvite).toHaveBeenCalledWith(ACESSO.id)
  })

  it('excluir pede confirmação antes', async () => {
    const servico = criarAcessosFalsos()
    const usuario = await montar(servico)

    await usuario.click(await screen.findByRole('button', { name: 'Excluir' }))
    expect(servico.excluir).not.toHaveBeenCalled()
    await usuario.click(screen.getByRole('button', { name: 'Confirmar exclusão' }))

    expect(servico.excluir).toHaveBeenCalledWith(ACESSO.id)
  })

  it('a gestão pública vê a lista sem os botões de alterar', async () => {
    const servico = criarAcessosFalsos({
      listar: vi.fn().mockResolvedValue({ podeAlterar: false, itens: [ACESSO] }),
    })
    await montar(servico)

    expect(await screen.findByText('Ana Souza')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Novo acesso' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Excluir' })).not.toBeInTheDocument()
    expect(screen.getByText(/Só o perfil Administração cria e altera acessos/)).toBeInTheDocument()
  })
})
