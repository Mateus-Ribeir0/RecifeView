import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { ContextoDasImportacoes } from '../../../application/importacoes/contexto'
import type { ServicoDeImportacoes } from '../../../application/importacoes/servico'
import { ErroDoRecifeView } from '../../../domain/erros'
import type { Pendencia } from '../../../domain/importacoes'
import { criarImportacao, criarServicoDeImportacoesFalso } from '../../../testes/importacaoFalsa'
import { PaginaHistorico } from './PaginaHistorico'
import { PaginaNovaImportacao } from './PaginaNovaImportacao'
import { PassoColunas } from './PassoColunas'
import { PassoPendencias } from './PassoPendencias'
import { PassoRevisao } from './PassoRevisao'
import { RelatorioDaImportacao } from './RelatorioDaImportacao'

function montar(servico: ServicoDeImportacoes, tela: ReactNode) {
  render(
    <MemoryRouter>
      <ContextoDasImportacoes value={servico}>{tela}</ContextoDasImportacoes>
    </MemoryRouter>,
  )
}

const BAIRRO_DESCONHECIDO: Pendencia = {
  tipo: 'bairro_desconhecido',
  campo: 'bairro',
  rotuloDoCampo: 'Bairro informado',
  quantidade: 3,
  valores: [{ valor: 'AFOGADOSS', quantidade: 3, sugestao: 'AFOGADOS' }],
  alternativas: ['AFOGADOS', 'VARZEA'],
  totalDeValores: 1,
  detalhes: {},
}

const COINCIDENCIA_CERTA: Pendencia = {
  tipo: 'coincidencias_certas',
  campo: null,
  rotuloDoCampo: null,
  quantidade: 1,
  valores: [
    {
      valor: 'Buraco na rua, Afogados: mesmo endereço, mesmo serviço, mesmo dia',
      quantidade: 1,
      sugestao: null,
    },
  ],
  alternativas: [],
  totalDeValores: 1,
  detalhes: {},
}

describe('pente fino entre canais', () => {
  it('pergunta o que fazer com o relato igual a um registro do arquivo', async () => {
    const servico = criarServicoDeImportacoesFalso()
    const base = criarImportacao({ status: 'AGUARDANDO_DECISOES' })
    const importacao = {
      ...base,
      pendencias: { ...base.pendencias, itens: [COINCIDENCIA_CERTA] },
    }
    montar(
      servico,
      <PassoPendencias importacao={importacao} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    expect(screen.getByText(/mesmo endereço, mesmo serviço/)).toBeInTheDocument()
    await userEvent.click(screen.getByLabelText(/Manter o registro oficial/))
    await userEvent.click(screen.getByRole('button', { name: 'Aplicar decisões' }))

    expect(servico.responderPendencias).toHaveBeenCalledWith(
      importacao.id,
      expect.objectContaining({ coincidenciasCertas: 'manter_o_registro_oficial' }),
    )
  })

  it('mostra na revisão que o arquivo foi comparado, mesmo sem coincidência', () => {
    const base = criarImportacao({ status: 'PRONTA' })
    const resumo = {
      ...base.pendencias.resumo,
      penteFino: { comparadas: 4, semEndereco: 1, certas: 0, provaveis: 0 },
    }
    const importacao = { ...base, pendencias: { ...base.pendencias, resumo } }
    montar(
      criarServicoDeImportacoesFalso(),
      <PassoRevisao importacao={importacao} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    expect(screen.getByText(/4 linhas comparadas com os relatos do formulário/)).toBeInTheDocument()
    expect(screen.getByText(/sem comparação de endereço/)).toBeVisible()
  })
})

describe('nova importação', () => {
  it('só envia depois de escolher o arquivo', async () => {
    const servico = criarServicoDeImportacoesFalso()
    montar(servico, <PaginaNovaImportacao />)

    expect(screen.queryByRole('button', { name: 'Enviar e analisar' })).not.toBeInTheDocument()

    const arquivo = new File(['a;b'], '156_2026.csv', { type: 'text/csv' })
    await userEvent.upload(screen.getByLabelText('Escolher arquivo'), arquivo)
    await userEvent.click(screen.getByRole('button', { name: 'Enviar e analisar' }))

    expect(servico.enviar).toHaveBeenCalledWith(arquivo)
  })

  it('mostra o motivo quando o envio falha', async () => {
    const servico = criarServicoDeImportacoesFalso()
    vi.mocked(servico.enviar).mockRejectedValue(
      new ErroDoRecifeView('erro_inesperado', 'O arquivo está vazio.'),
    )
    montar(servico, <PaginaNovaImportacao />)

    await userEvent.upload(screen.getByLabelText('Escolher arquivo'), new File([''], 'a.csv'))
    await userEvent.click(screen.getByRole('button', { name: 'Enviar e analisar' }))

    expect(await screen.findByText('O arquivo está vazio.')).toBeInTheDocument()
  })
})

describe('colunas', () => {
  it('esconde os valores de coluna bloqueada e diz o motivo', async () => {
    montar(
      criarServicoDeImportacoesFalso(),
      <PassoColunas importacao={criarImportacao()} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    const linha = screen.getByRole('row', { name: /CPF/ })
    expect(within(linha).getByText('oculto')).toBeInTheDocument()
    expect(within(linha).getByText('Bloqueada: Documento pessoal')).toBeInTheDocument()
    expect(within(linha).getByText('Descartada')).toBeInTheDocument()
    expect(within(linha).queryByRole('combobox')).not.toBeInTheDocument()
  })

  it('pede uma saída quando falta campo obrigatório', async () => {
    const colunas = criarImportacao().estrutura.colunas.filter((coluna) => coluna.nome !== 'GRUPO')
    const importacao = criarImportacao({
      estrutura: { ...criarImportacao().estrutura, colunas },
    })
    montar(
      criarServicoDeImportacoesFalso(),
      <PassoColunas importacao={importacao} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    expect(screen.getByText('Faltam campos obrigatórios')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Conferir os dados' })).toBeDisabled()

    await userEvent.type(screen.getByLabelText('Valor fixo para Categoria'), 'DRENAGEM')

    expect(screen.getByRole('button', { name: 'Conferir os dados' })).toBeEnabled()
  })

  it('não deixa conferir sem escolher a fonte', async () => {
    const base = criarImportacao()
    const importacao = criarImportacao({
      layout: 'manual',
      fonte: null,
      decisoes: { ...base.decisoes, fonte: null },
    })
    montar(
      criarServicoDeImportacoesFalso(),
      <PassoColunas importacao={importacao} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    expect(screen.getByText('Falta escolher a fonte')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Conferir os dados' })).toBeDisabled()

    await userEvent.selectOptions(
      screen.getByLabelText('De qual fonte é este arquivo?'),
      '156_EMLURB',
    )

    expect(screen.queryByText('Falta escolher a fonte')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Conferir os dados' })).toBeEnabled()
  })

  it('envia a escolha de colunas', async () => {
    const servico = criarServicoDeImportacoesFalso()
    const aoConcluir = vi.fn()
    montar(
      servico,
      <PassoColunas importacao={criarImportacao()} aoConcluir={aoConcluir} aoCancelar={vi.fn()} />,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Conferir os dados' }))

    expect(servico.definirColunas).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ fonte: '156_EMLURB', dataDoRetrato: '2026-11-05' }),
    )
    expect(aoConcluir).toHaveBeenCalled()
  })

  it('avisa quando o mesmo arquivo já entrou', () => {
    const estrutura = {
      ...criarImportacao().estrutura,
      mesmoArquivo: [{ id: 1, criadaEm: '2026-10-07T10:00:00Z', status: 'CONCLUIDA' }],
    }
    montar(
      criarServicoDeImportacoesFalso(),
      <PassoColunas
        importacao={criarImportacao({ estrutura })}
        aoConcluir={vi.fn()}
        aoCancelar={vi.fn()}
      />,
    )

    expect(screen.getByText('Este arquivo já foi importado')).toBeInTheDocument()
  })
})

describe('decisões', () => {
  function importacaoComPendencia(...itens: Pendencia[]) {
    const base = criarImportacao()
    return criarImportacao({
      status: 'AGUARDANDO_DECISOES',
      pendencias: { ...base.pendencias, itens },
    })
  }

  it('já traz a sugestão escolhida e manda a decisão', async () => {
    const servico = criarServicoDeImportacoesFalso()
    montar(
      servico,
      <PassoPendencias
        importacao={importacaoComPendencia(BAIRRO_DESCONHECIDO)}
        aoConcluir={vi.fn()}
        aoCancelar={vi.fn()}
      />,
    )

    expect(screen.getByLabelText('O que fazer com AFOGADOSS')).toHaveValue('AFOGADOS')

    await userEvent.click(screen.getByRole('button', { name: 'Aplicar decisões' }))

    expect(servico.responderPendencias).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ substituicoes: { bairro: { AFOGADOSS: 'AFOGADOS' } } }),
    )
  })

  it('pergunta o que fazer com os registros que já existem', async () => {
    const servico = criarServicoDeImportacoesFalso()
    const repetidos: Pendencia = {
      ...BAIRRO_DESCONHECIDO,
      tipo: 'repetidos_na_base',
      campo: null,
      quantidade: 12,
      valores: [],
      detalhes: { iguais: 3, alteradas: 12 },
    }
    montar(
      servico,
      <PassoPendencias
        importacao={importacaoComPendencia(repetidos)}
        aoConcluir={vi.fn()}
        aoCancelar={vi.fn()}
      />,
    )

    await userEvent.click(screen.getByLabelText(/Atualizar com a versão deste arquivo/))
    await userEvent.click(screen.getByRole('button', { name: 'Aplicar decisões' }))

    expect(servico.responderPendencias).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ repetidosNaBase: 'atualizar' }),
    )
  })
})

describe('revisão', () => {
  it('mostra a conta final antes de gravar', async () => {
    const servico = criarServicoDeImportacoesFalso()
    const importacao = criarImportacao({ status: 'PRONTA' })
    montar(
      servico,
      <PassoRevisao importacao={importacao} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    expect(screen.getByText('Entram como novas')).toBeInTheDocument()
    expect(screen.getByText('Linhas quebradas: 1')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Confirmar a carga' }))

    expect(servico.confirmar).toHaveBeenCalledWith(7)
  })

  it('avisa quando faltar o sal do pseudônimo', () => {
    const base = criarImportacao({ status: 'PRONTA' })
    const importacao = {
      ...base,
      pendencias: { ...base.pendencias, resumo: { ...base.pendencias.resumo, semIdLocal: 9 } },
    }
    montar(
      criarServicoDeImportacoesFalso(),
      <PassoRevisao importacao={importacao} aoConcluir={vi.fn()} aoCancelar={vi.fn()} />,
    )

    expect(screen.getByText('Registros fora da reincidência')).toBeInTheDocument()
  })
})

describe('relatório', () => {
  it('pede confirmação antes de desfazer', async () => {
    const servico = criarServicoDeImportacoesFalso()
    const importacao = criarImportacao({ status: 'CONCLUIDA', podeDesfazer: true })
    montar(servico, <RelatorioDaImportacao importacao={importacao} aoMudar={vi.fn()} />)

    await userEvent.click(screen.getByRole('button', { name: 'Desfazer esta importação' }))
    expect(servico.desfazer).not.toHaveBeenCalled()

    await userEvent.click(screen.getByRole('button', { name: 'Sim, desfazer' }))
    expect(servico.desfazer).toHaveBeenCalledWith(7)
  })

  it('não oferece desfazer quando não é a última', () => {
    const importacao = criarImportacao({ status: 'CONCLUIDA', podeDesfazer: false })
    montar(
      criarServicoDeImportacoesFalso(),
      <RelatorioDaImportacao importacao={importacao} aoMudar={vi.fn()} />,
    )

    expect(screen.queryByRole('button', { name: /Desfazer/ })).not.toBeInTheDocument()
  })

  it('diz que o arquivo com dado sensível foi apagado', () => {
    const importacao = criarImportacao({ status: 'CONCLUIDA', arquivoGuardado: false })
    montar(
      criarServicoDeImportacoesFalso(),
      <RelatorioDaImportacao importacao={importacao} aoMudar={vi.fn()} />,
    )

    expect(screen.getByText(/apagado depois da carga/)).toBeInTheDocument()
  })
})

describe('histórico', () => {
  it('lista a importação com arquivo, autoria e situação', async () => {
    montar(criarServicoDeImportacoesFalso(), <PaginaHistorico />)

    expect(await screen.findByRole('link', { name: '156_2026.csv' })).toBeInTheDocument()
    expect(screen.getByText('Gestora de Demonstração')).toBeInTheDocument()
  })
})
