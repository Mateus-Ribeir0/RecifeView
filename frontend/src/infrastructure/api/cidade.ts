import type { ServicoDaCidade } from '../../application/cidade/servico'
import type { IndicadoresDoBairro, MeuRelato, OcorrenciaDaCidade } from '../../domain/cidade'
import type { ClienteHttp } from './cliente'
import { converterChaves } from './conversao'

const BASE = '/cidade'

export function criarServicoDaCidade(cliente: ClienteHttp): ServicoDaCidade {
  async function ler<T>(caminho: string): Promise<T> {
    return converterChaves<T>(await cliente.enviar<unknown>(caminho, { autenticada: true }))
  }

  return {
    ocorrencias: ({ bairro, tema }) => {
      const params = new URLSearchParams()
      if (bairro) params.set('bairro', bairro)
      if (tema) params.set('tema', tema)
      const consulta = params.size ? `?${params}` : ''
      return ler<OcorrenciaDaCidade[]>(`${BASE}/ocorrencias${consulta}`)
    },
    meuBairro: (bairro) =>
      ler<IndicadoresDoBairro>(`${BASE}/bairros/${encodeURIComponent(bairro)}`),
    meusRelatos: () => ler<MeuRelato[]>(`${BASE}/meus-relatos`),
  }
}
