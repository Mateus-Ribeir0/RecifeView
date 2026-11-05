import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { Funil } from '../../charts/Funil'
import { Abas } from '../../components/Abas'
import { filtrosDaRota } from '../../conteudo/telasDoPainel'
import { resumirEscolha } from './resumirEscolha'

const OPCOES = [
  { valor: '1', rotulo: 'RPA 1 (Centro)' },
  { valor: '2', rotulo: 'RPA 2 (Norte)' },
]

describe('filtros de cada tela', () => {
  it('mostra todos os filtros nas telas que aceitam recorte', () => {
    expect(filtrosDaRota('/painel/prazos')).toEqual(['periodo', 'rpa', 'bairro', 'categoria'])
  })

  it('tira o período da Prioridade, que usa período fixo', () => {
    expect(filtrosDaRota('/painel/prioridade')).not.toContain('periodo')
  })

  it('não mostra filtros onde eles não se aplicam', () => {
    expect(filtrosDaRota('/painel/war-room')).toEqual([])
    expect(filtrosDaRota('/painel/importacoes/7')).toEqual([])
  })
})

describe('resumo do filtro', () => {
  it('diz o nome quando há uma escolha e a quantidade quando há várias', () => {
    expect(resumirEscolha([], OPCOES, 'Todas')).toBe('Todas')
    expect(resumirEscolha(['2'], OPCOES, 'Todas')).toBe('RPA 2 (Norte)')
    expect(resumirEscolha(['1', '2'], OPCOES, 'Todas')).toBe('2 escolhidos')
  })
})

describe('abas', () => {
  const ABAS = [
    { chave: 'a', rotulo: 'Primeira', conteudo: <p>Conteúdo A</p> },
    { chave: 'b', rotulo: 'Segunda', conteudo: <p>Conteúdo B</p> },
  ]

  it('troca o conteúdo pelo clique', async () => {
    render(<Abas legenda="Partes" abas={ABAS} />)

    await userEvent.click(screen.getByRole('tab', { name: 'Segunda' }))

    expect(screen.getByText('Conteúdo B')).toBeInTheDocument()
    expect(screen.queryByText('Conteúdo A')).not.toBeInTheDocument()
  })

  it('anda com as setas do teclado', async () => {
    render(<Abas legenda="Partes" abas={ABAS} />)

    screen.getByRole('tab', { name: 'Primeira' }).focus()
    await userEvent.keyboard('{ArrowRight}')

    expect(screen.getByRole('tab', { name: 'Segunda' })).toHaveFocus()
    expect(screen.getByText('Conteúdo B')).toBeInTheDocument()
  })
})

describe('funil', () => {
  it('mostra quanto se perde entre as etapas', () => {
    render(
      <Funil
        etapas={[
          { chave: 'a', rotulo: 'Entraram', valor: 100 },
          { chave: 'b', rotulo: 'Saíram', valor: 25 },
        ]}
      />,
    )

    expect(screen.getByText(/75 ficam pelo caminho/)).toBeInTheDocument()
  })
})
