import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDoPainel } from '../../../application/consultas/ProvedorDoPainel'
import type { ServicoDoPainel } from '../../../application/consultas/servico'
import { ContextoDosEncaminhamentos } from '../../../application/encaminhamentos/contexto'
import type { ServicoDeEncaminhamentos } from '../../../application/encaminhamentos/servico'
import {
  CHAVE_LONGA,
  criarEncaminhamentosFalsos,
  ENCAMINHAMENTO,
  PREPARO,
} from '../../../testes/encaminhamentoFalso'
import { PainelDeEncaminhamento } from './PainelDeEncaminhamento'

const PAINEL = {
  catalogo: vi
    .fn()
    .mockResolvedValue({ bairros: [{ bairroOficial: 'AFOGADOS', nome: 'Afogados' }] }),
} as unknown as ServicoDoPainel

function montar(servico: ServicoDeEncaminhamentos, aoConcluir = vi.fn()) {
  render(
    <MemoryRouter>
      <ProvedorDoPainel servico={PAINEL}>
        <ContextoDosEncaminhamentos value={servico}>
          <PainelDeEncaminhamento
            chaveRegistro={CHAVE_LONGA}
            nota={8.4}
            aoFechar={vi.fn()}
            aoConcluir={aoConcluir}
          />
        </ContextoDosEncaminhamentos>
      </ProvedorDoPainel>
    </MemoryRouter>,
  )
  return userEvent.setup()
}

describe('painel de encaminhamento', () => {
  it('mostra a sugestão com a evidência do tema', async () => {
    montar(criarEncaminhamentosFalsos())

    expect(await screen.findByText('Sugestão: Compesa')).toBeInTheDocument()
    expect(screen.getByText(/80,0% citam Emlurb/)).toBeInTheDocument()
    expect(screen.getByLabelText('Órgão que vai receber')).toHaveValue('COMPESA')
  })

  it('encaminha para o órgão escolhido com a chave inteira', async () => {
    const encaminhar = vi.fn().mockResolvedValue(ENCAMINHAMENTO)
    const aoConcluir = vi.fn()
    const usuario = montar(criarEncaminhamentosFalsos({ encaminhar }), aoConcluir)

    await usuario.selectOptions(await screen.findByLabelText('Órgão que vai receber'), 'EMLURB')
    await usuario.type(screen.getByLabelText(/Por que encaminhar/), 'Ponto crônico')
    await usuario.click(screen.getByRole('button', { name: 'Encaminhar para Emlurb' }))

    expect(encaminhar).toHaveBeenCalledWith({
      chaveRegistro: CHAVE_LONGA,
      orgao: 'EMLURB',
      justificativa: 'Ponto crônico',
      nota: 8.4,
    })
    expect(aoConcluir).toHaveBeenCalledWith(ENCAMINHAMENTO)
  })

  it('não deixa encaminhar de novo o que já está com um órgão', async () => {
    const preparar = vi.fn().mockResolvedValue({
      ...PREPARO,
      podeEncaminhar: false,
      encaminhamentos: [ENCAMINHAMENTO],
    })
    montar(criarEncaminhamentosFalsos({ preparar }))

    expect(await screen.findByText('Esta ocorrência já está com um órgão')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Encaminhar/ })).not.toBeInTheDocument()
  })
})
