import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../../../application/autenticacao/ProvedorDeSessao'
import type { ServicoDeAutenticacao } from '../../../../application/autenticacao/servico'
import { ContextoDasContribuicoes } from '../../../../application/contribuicoes/contexto'
import type { ServicoDeContribuicoes } from '../../../../application/contribuicoes/servico'
import { ErroDoRecifeView } from '../../../../domain/erros'
import { criarContribuicoesFalsas } from '../../../../testes/contribuicaoFalsa'
import { CIDADA, criarServicoFalso } from '../../../../testes/servicoFalso'
import { FormularioDeRelato } from './FormularioDeRelato'

function montar(
  servico: ServicoDeContribuicoes,
  sessao: ServicoDeAutenticacao = criarServicoFalso(),
) {
  render(
    <MemoryRouter>
      <ProvedorDeSessao servico={sessao}>
        <ContextoDasContribuicoes value={servico}>
          <FormularioDeRelato />
        </ContextoDasContribuicoes>
      </ProvedorDeSessao>
    </MemoryRouter>,
  )
  return userEvent.setup()
}

type Usuario = ReturnType<typeof userEvent.setup>

async function preencherAteOEnvio(usuario: Usuario) {
  await usuario.click(await screen.findByLabelText('Buraco na rua'))
  await usuario.click(screen.getByRole('button', { name: 'Continuar' }))
  await usuario.selectOptions(await screen.findByLabelText('Bairro'), 'AFOGADOS')
  await usuario.type(screen.getByLabelText('Rua'), 'Rua Fictícia')
  await usuario.click(screen.getByRole('button', { name: 'Continuar' }))
}

describe('formulário de relato', () => {
  it('não avança sem escolher o problema', async () => {
    const usuario = montar(criarContribuicoesFalsas())

    await usuario.click(await screen.findByRole('button', { name: 'Continuar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Escolha o que está acontecendo.')
  })

  it('com a conta de cidadão aberta, leva para Meus relatos', async () => {
    const sessao = criarServicoFalso({ restaurarSessao: vi.fn().mockResolvedValue(CIDADA) })
    const usuario = montar(criarContribuicoesFalsas(), sessao)

    await preencherAteOEnvio(usuario)
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Enviar relato' }))

    const link = await screen.findByRole('link', { name: 'Acompanhar em Meus relatos' })
    expect(link).toHaveAttribute('href', '/cidade/meus-relatos')
  })

  it('envia com uma chave e mostra que o relato foi recebido', async () => {
    const enviar = vi.fn().mockResolvedValue('nova')
    const usuario = montar(criarContribuicoesFalsas({ enviar }))

    await preencherAteOEnvio(usuario)
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Enviar relato' }))

    expect(await screen.findByRole('heading', { name: 'Relato recebido' })).toBeInTheDocument()
    expect(enviar).toHaveBeenCalledTimes(1)
    expect(enviar.mock.calls[0]?.[0]).toMatchObject({
      servicoCodigo: '131',
      bairroOficial: 'AFOGADOS',
      logradouro: 'Rua Fictícia',
      site: '',
    })
    expect(enviar.mock.calls[0]?.[0].chaveDeEnvio).toMatch(/^[0-9a-f]{32}$/)
  })

  it('diz que o relato foi somado quando outra pessoa já relatou', async () => {
    const usuario = montar(
      criarContribuicoesFalsas({ enviar: vi.fn().mockResolvedValue('somada') }),
    )

    await preencherAteOEnvio(usuario)
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Enviar relato' }))

    const resultado = await screen.findByRole('status')
    expect(within(resultado).getByRole('heading')).toHaveTextContent(
      'Outra pessoa já relatou este problema',
    )
  })

  it('exige confirmar o aviso antes de enviar', async () => {
    const enviar = vi.fn()
    const usuario = montar(criarContribuicoesFalsas({ enviar }))

    await preencherAteOEnvio(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Enviar relato' }))

    expect(await screen.findByText('Confirme que leu o aviso para enviar.')).toBeInTheDocument()
    expect(enviar).not.toHaveBeenCalled()
  })

  it('mostra no campo o dado pessoal recusado pelo servidor', async () => {
    const recusa = new ErroDoRecifeView(
      'contribuicao_invalida',
      'Parece haver CPF, telefone ou e-mail neste campo.',
      null,
      'detalhe',
    )
    const usuario = montar(criarContribuicoesFalsas({ enviar: vi.fn().mockRejectedValue(recusa) }))

    await preencherAteOEnvio(usuario)
    await usuario.click(screen.getByRole('checkbox'))
    await usuario.click(screen.getByRole('button', { name: 'Enviar relato' }))

    expect(await screen.findByText(recusa.message)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Enviar relato' })).toBeEnabled()
  })

  it('avisa quando o formulário não consegue abrir', async () => {
    const falha = new ErroDoRecifeView('servico_indisponivel', 'Servidor fora do ar.')
    montar(criarContribuicoesFalsas({ catalogo: vi.fn().mockRejectedValue(falha) }))

    expect(await screen.findByText('Servidor fora do ar.')).toBeInTheDocument()
  })
})
