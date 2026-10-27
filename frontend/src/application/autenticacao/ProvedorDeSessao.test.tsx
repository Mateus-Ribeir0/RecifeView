import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { criarServicoFalso, GESTORA } from '../../testes/servicoFalso'
import type { EstadoDaSessao } from './contexto'
import { ProvedorDeSessao } from './ProvedorDeSessao'
import type { ServicoDeAutenticacao } from './servico'
import { useSessao } from './useSessao'

function descrever(estado: EstadoDaSessao): string {
  if (estado.situacao === 'autenticada') return `autenticada:${estado.usuario.nome}`
  if (estado.situacao === 'anonima') return `anonima:${estado.motivo ?? 'nenhum'}`
  return 'verificando'
}

function Espiao() {
  const { estado, entrar, sair } = useSessao()
  return (
    <>
      <p>{descrever(estado)}</p>
      <button onClick={() => entrar({ email: GESTORA.email, senha: 'qualquer' })}>entrar</button>
      <button onClick={() => sair()}>sair</button>
    </>
  )
}

function renderizar(servico: ServicoDeAutenticacao) {
  return render(
    <ProvedorDeSessao servico={servico}>
      <Espiao />
    </ProvedorDeSessao>,
  )
}

describe('ProvedorDeSessao', () => {
  it('começa verificando e fica anônimo sem sessão salva', async () => {
    renderizar(criarServicoFalso())
    expect(screen.getByText('verificando')).toBeInTheDocument()
    expect(await screen.findByText('anonima:nenhum')).toBeInTheDocument()
  })

  it('restaura a sessão existente', async () => {
    renderizar(criarServicoFalso({ restaurarSessao: () => Promise.resolve(GESTORA) }))
    expect(await screen.findByText('autenticada:Gestora de Teste')).toBeInTheDocument()
  })

  it('entra e sai', async () => {
    renderizar(criarServicoFalso())
    await screen.findByText('anonima:nenhum')

    await userEvent.click(screen.getByRole('button', { name: 'entrar' }))
    expect(await screen.findByText('autenticada:Gestora de Teste')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'sair' }))
    expect(await screen.findByText('anonima:saiu')).toBeInTheDocument()
  })

  it('marca a sessão como expirada quando o serviço avisa a perda', async () => {
    let avisarPerda: () => void = () => undefined
    const servico = criarServicoFalso({
      restaurarSessao: () => Promise.resolve(GESTORA),
      observarPerdaDeSessao: (aoPerder) => {
        avisarPerda = aoPerder
        return () => undefined
      },
    })
    renderizar(servico)
    await screen.findByText('autenticada:Gestora de Teste')

    act(() => avisarPerda())

    await waitFor(() => expect(screen.getByText('anonima:sessao-expirada')).toBeInTheDocument())
  })
})
