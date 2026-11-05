import type { PedidoDeFila, ServicoDoPainel } from '../../application/consultas/servico'
import type { Filtros } from '../../domain/filtros'
import type {
  CanaisDaOuvidoria,
  CatalogoDeFiltros,
  Consulta,
  Prazos,
  Recorrencias,
  Retorno,
  SobreOsDados,
  Territorio,
  VisaoGeral,
} from '../../domain/painel'
import type { Criterios, FilaClassificada, Julgamento, Prioridade } from '../../domain/prioridade'
import type { CalendarioDaWarRoom, QuadroDoDia } from '../../domain/warRoom'
import type { ClienteHttp } from './cliente'
import { converterChaves } from './conversao'

function paramsDosFiltros(filtros: Filtros): URLSearchParams {
  const params = new URLSearchParams({
    periodo_inicio: `${filtros.anoInicio}-01`,
    periodo_fim: `${filtros.anoFim}-12`,
  })
  filtros.rpas.forEach((rpa) => params.append('rpa', rpa))
  filtros.bairros.forEach((bairro) => params.append('bairro', bairro))
  filtros.categorias.forEach((categoria) => params.append('categoria', categoria))
  return params
}

function julgamentosEmJson(julgamentos: readonly Julgamento[]) {
  return { julgamentos }
}

export function criarServicoDoPainel(cliente: ClienteHttp): ServicoDoPainel {
  async function ler<T>(caminho: string): Promise<T> {
    return converterChaves<T>(await cliente.enviar<unknown>(caminho, { autenticada: true }))
  }

  async function postar<T>(caminho: string, corpo: unknown): Promise<T> {
    const resposta = await cliente.enviar<unknown>(caminho, {
      metodo: 'POST',
      corpo,
      autenticada: true,
    })
    return converterChaves<T>(resposta)
  }

  function comFiltros<T>(caminho: string, filtros: Filtros, extra?: Record<string, string>) {
    const params = paramsDosFiltros(filtros)
    Object.entries(extra ?? {}).forEach(([chave, valor]) => params.set(chave, valor))
    return ler<Consulta<T>>(`${caminho}?${params}`)
  }

  return {
    catalogo: () => ler<CatalogoDeFiltros>('/catalogos/filtros'),
    visaoGeral: (filtros) => comFiltros<VisaoGeral>('/indicadores/visao-geral', filtros),
    retorno: (filtros) => comFiltros<Retorno>('/retorno/indicacoes', filtros),
    ouvidoria: (filtros) => comFiltros<CanaisDaOuvidoria>('/retorno/ouvidoria', filtros),
    recorrencias: (filtros, semGenerico) =>
      comFiltros<Recorrencias>('/recorrencias', filtros, { sem_generico: String(semGenerico) }),
    prazos: (filtros, semMesmoDia) =>
      comFiltros<Prazos>('/prazos', filtros, { sem_mesmo_dia: String(semMesmoDia) }),
    territorio: (filtros) => comFiltros<Territorio>('/territorio/bairros', filtros),
    criterios: () => ler<Criterios>('/prioridade/criterios'),
    prioridade: (julgamentos) =>
      postar<Prioridade>('/prioridade/indice', julgamentosEmJson(julgamentos)),
    fila: ({ fonte, julgamentos, semente, filtros }: PedidoDeFila) =>
      postar<FilaClassificada>(`/prioridade/fila?${paramsDosFiltros(filtros)}`, {
        fonte,
        semente,
        ...julgamentosEmJson(julgamentos),
      }),
    calendario: () => ler<CalendarioDaWarRoom>('/war-room/calendario'),
    quadroDoDia: (dia, inicioDaSerie) => {
      const params = new URLSearchParams({ data: dia })
      if (inicioDaSerie) params.set('inicio_da_serie', inicioDaSerie)
      return ler<QuadroDoDia>(`/war-room/dia?${params}`)
    },
    sobre: () => ler<SobreOsDados>('/sobre'),
  }
}
