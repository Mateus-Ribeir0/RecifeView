import { describe, expect, it, vi } from 'vitest'

import { FILTROS_PADRAO } from '../../domain/filtros'
import type { ClienteHttp } from './cliente'
import { converterChaves } from './conversao'
import { criarServicoDeImportacoes } from './importacoes'
import { criarServicoDoPainel } from './painel'

function clienteFalso(resposta: unknown = {}) {
  const enviar = vi.fn().mockResolvedValue(resposta)
  return { cliente: { enviar } as unknown as ClienteHttp, enviar }
}

describe('conversão do JSON da API', () => {
  it('passa as chaves para camelCase em qualquer nível', () => {
    const json = { pct_enviadas: 97, por_ano: [{ dias_ate_envio: 9 }] }

    expect(converterChaves(json)).toEqual({ pctEnviadas: 97, porAno: [{ diasAteEnvio: 9 }] })
  })

  it('converte chave com número', () => {
    expect(converterChaves({ faixas_156: 1 })).toEqual({ faixas156: 1 })
  })

  it('não mexe em dicionários de dados', () => {
    const json = { mapeamento: { data_demanda: 'data_abertura' } }

    expect(converterChaves(json, new Set(['mapeamento']))).toEqual({
      mapeamento: { data_demanda: 'data_abertura' },
    })
  })
})

describe('serviço do painel', () => {
  it('monta os filtros globais na URL', async () => {
    const { cliente, enviar } = clienteFalso()

    await criarServicoDoPainel(cliente).visaoGeral({
      ...FILTROS_PADRAO,
      rpas: ['1', '2'],
      bairros: ['VARZEA'],
      categorias: ['DRENAGEM'],
    })

    const caminho = String(enviar.mock.calls[0]?.[0])
    expect(caminho).toContain('/indicadores/visao-geral?')
    expect(caminho).toContain('periodo_inicio=2021-01')
    expect(caminho).toContain('periodo_fim=2025-12')
    expect(caminho).toContain('rpa=1&rpa=2')
    expect(caminho).toContain('bairro=VARZEA')
    expect(caminho).toContain('categoria=DRENAGEM')
  })

  it('leva a alternância de endereços genéricos', async () => {
    const { cliente, enviar } = clienteFalso()

    await criarServicoDoPainel(cliente).recorrencias(FILTROS_PADRAO, true)

    expect(String(enviar.mock.calls[0]?.[0])).toContain('sem_generico=true')
  })
})

describe('serviço de importações', () => {
  it('envia o arquivo sem transformar e com o nome na URL', async () => {
    const { cliente, enviar } = clienteFalso({ id: 1 })
    const arquivo = new File(['a;b'], '156 2026.csv')

    await criarServicoDeImportacoes(cliente).enviar(arquivo)

    expect(enviar).toHaveBeenCalledWith(
      '/importacoes?nome=156+2026.csv',
      expect.objectContaining({ metodo: 'POST', arquivo, autenticada: true }),
    )
  })

  it('não altera os nomes de coluna do arquivo', async () => {
    const { cliente } = clienteFalso({
      decisoes: { mapeamento: { DATA_DEMANDA: 'data_abertura' } },
    })

    const detalhe = await criarServicoDeImportacoes(cliente).consultar(1)

    expect(detalhe.decisoes.mapeamento).toEqual({ DATA_DEMANDA: 'data_abertura' })
  })

  it('responde as pendências em snake_case', async () => {
    const { cliente, enviar } = clienteFalso()

    await criarServicoDeImportacoes(cliente).responderPendencias(1, {
      repetidosNaBase: 'atualizar',
    })

    expect(enviar.mock.calls[0]?.[1]).toMatchObject({
      metodo: 'PUT',
      corpo: { repetidos_na_base: 'atualizar' },
    })
  })
})
