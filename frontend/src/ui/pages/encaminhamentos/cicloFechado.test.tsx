import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { createMemoryRouter, MemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ProvedorDoPainel } from '../../../application/consultas/ProvedorDoPainel'
import type { ServicoDoPainel } from '../../../application/consultas/servico'
import { ContextoDosEncaminhamentos } from '../../../application/encaminhamentos/contexto'
import type { ServicoDeEncaminhamentos } from '../../../application/encaminhamentos/servico'
import type { OcorrenciaDoPainel } from '../../../domain/contribuicoes'
import {
  CHAVE_LONGA,
  criarEncaminhamentosFalsos,
  ENCAMINHAMENTO,
} from '../../../testes/encaminhamentoFalso'
import { ListaDeOcorrencias } from '../contribuicoes/ListaDeOcorrencias'
import { BarraLateral } from '../painel/BarraLateral'
import { PaginaDoEncaminhamento } from './PaginaDoEncaminhamento'

const PAINEL = {
  catalogo: vi
    .fn()
    .mockResolvedValue({ fontes: [], bairros: [], anoMinimo: 2012, anoMaximo: 2026 }),
} as unknown as ServicoDoPainel

function comProvedores(servico: ServicoDeEncaminhamentos, tela: ReactNode) {
  return (
    <ProvedorDoPainel servico={PAINEL}>
      <ContextoDosEncaminhamentos value={servico}>{tela}</ContextoDosEncaminhamentos>
    </ProvedorDoPainel>
  )
}

const RELATO_NA_BASE: OcorrenciaDoPainel = {
  id: '6f1c2b8e-0000-4000-8000-0000000000aa',
  recebidaEm: '2026-11-01T10:00:00Z',
  servico: 'Buraco na rua',
  bairro: 'Afogados',
  logradouro: 'RUA FICTICIA',
  numero: '120',
  relatos: 3,
  semRetorno: 1,
  situacao: 'na_base',
  chaveRegistro: CHAVE_LONGA,
  encaminhamento: null,
}

describe('ciclo fechado', () => {
  it('o menu conta o que pede ação da gestão', async () => {
    render(
      <MemoryRouter initialEntries={['/painel']}>
        {comProvedores(
          criarEncaminhamentosFalsos(),
          <BarraLateral recolhida={false} aoNavegar={vi.fn()} />,
        )}
      </MemoryRouter>,
    )

    expect(await screen.findByText(', 3 encaminhamentos pedem ação')).toBeInTheDocument()
    expect(screen.getByText(', 4 duplas esperam o pente fino')).toBeInTheDocument()
  })

  it('o detalhe do devolvido leva a outro órgão', async () => {
    const devolvido = { ...ENCAMINHAMENTO, situacao: 'devolvido' as const }
    const servico = criarEncaminhamentosFalsos({ consultar: vi.fn().mockResolvedValue(devolvido) })
    const roteador = createMemoryRouter(
      [{ path: '/painel/encaminhamentos/:id', element: <PaginaDoEncaminhamento /> }],
      { initialEntries: ['/painel/encaminhamentos/1'] },
    )
    await act(async () => {
      render(comProvedores(servico, <RouterProvider router={roteador} />))
    })

    await userEvent.click(
      await screen.findByRole('button', { name: 'Encaminhar para outro órgão' }),
    )

    expect(await screen.findByText('Para quem vai esta ocorrência?')).toBeInTheDocument()
    expect(servico.preparar).toHaveBeenCalledWith(CHAVE_LONGA)
  })

  it('o relato que já está na base segue para o órgão com o vínculo do relato', async () => {
    const servico = criarEncaminhamentosFalsos()
    const aoEncaminhar = vi.fn()
    render(
      <MemoryRouter>
        {comProvedores(
          servico,
          <ListaDeOcorrencias
            pagina={{ itens: [RELATO_NA_BASE], total: 1 }}
            deslocamento={0}
            aoMudarDeslocamento={vi.fn()}
            aoEncaminhar={aoEncaminhar}
          />,
        )}
      </MemoryRouter>,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Encaminhar' }))
    await userEvent.click(await screen.findByRole('button', { name: 'Encaminhar para Compesa' }))

    expect(servico.encaminhar).toHaveBeenCalledWith(
      expect.objectContaining({ chaveRegistro: CHAVE_LONGA, contribuicaoId: RELATO_NA_BASE.id }),
    )
    expect(aoEncaminhar).toHaveBeenCalled()
  })
})
