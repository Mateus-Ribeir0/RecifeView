import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDeSessao } from '../../../application/autenticacao/ProvedorDeSessao'
import { ContextoDasContribuicoes } from '../../../application/contribuicoes/contexto'
import { criarContribuicoesFalsas } from '../../../testes/contribuicaoFalsa'
import { CIDADA, criarServicoFalso } from '../../../testes/servicoFalso'
import { PaginaMinhaConta } from './PaginaMinhaConta'

describe('minha conta', () => {
  it('desliga os avisos por e-mail', async () => {
    const servico = criarServicoFalso({ restaurarSessao: vi.fn().mockResolvedValue(CIDADA) })
    render(
      <MemoryRouter>
        <ProvedorDeSessao servico={servico}>
          <ContextoDasContribuicoes value={criarContribuicoesFalsas()}>
            <PaginaMinhaConta />
          </ContextoDasContribuicoes>
        </ProvedorDeSessao>
      </MemoryRouter>,
    )
    const marcacao = await screen.findByRole('checkbox', { name: /Avisar por e-mail/ })

    expect(marcacao).toBeChecked()
    await userEvent.click(marcacao)

    expect(servico.definirAvisos).toHaveBeenCalledWith(false)
    expect(await screen.findByRole('checkbox', { name: /Avisar por e-mail/ })).not.toBeChecked()
  })
})
