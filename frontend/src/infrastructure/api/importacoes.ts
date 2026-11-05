import type { ServicoDeImportacoes } from '../../application/importacoes/servico'
import type {
  CampoDaBase,
  DetalheDaImportacao,
  EscolhaDeColunas,
  PaginaDeImportacoes,
  PaginaDeRegistros,
  RespostasDePendencias,
  ResumoDaImportacao,
} from '../../domain/importacoes'
import type { ClienteHttp } from './cliente'
import { converterChaves } from './conversao'

const REGISTROS_POR_PAGINA = 50
const IMPORTACOES_POR_PAGINA = 50
const BASE = '/importacoes'

// Nomes de coluna do arquivo e valores de domínio: viraram chave de dicionário, não de contrato.
const CHAVES_OPACAS: ReadonlySet<string> = new Set([
  'mapeamento',
  'valores_fixos',
  'substituicoes',
  'padrao_para_valores',
  'antes',
  'depois',
  'descartes',
  'correcoes',
  'fontes',
  'detalhes',
])

function respostasEmJson(respostas: RespostasDePendencias) {
  return {
    formato_de_data: respostas.formatoDeData,
    substituicoes: respostas.substituicoes,
    padrao_para_valores: respostas.padraoParaValores,
    datas_invalidas: respostas.datasInvalidas,
    repetidos_na_base: respostas.repetidosNaBase,
    repetidos_no_arquivo: respostas.repetidosNoArquivo,
  }
}

export function criarServicoDeImportacoes(cliente: ClienteHttp): ServicoDeImportacoes {
  async function ler<T>(caminho: string): Promise<T> {
    const resposta = await cliente.enviar<unknown>(caminho, { autenticada: true })
    return converterChaves<T>(resposta, CHAVES_OPACAS)
  }

  async function mudar(caminho: string, metodo: 'POST' | 'PUT', corpo?: unknown) {
    const resposta = await cliente.enviar<unknown>(caminho, { metodo, corpo, autenticada: true })
    return converterChaves<ResumoDaImportacao>(resposta, CHAVES_OPACAS)
  }

  return {
    campos: () => ler<CampoDaBase[]>(`${BASE}/campos`),
    listar: ({ busca, situacao, deslocamento }) => {
      const params = new URLSearchParams({
        limite: String(IMPORTACOES_POR_PAGINA),
        deslocamento: String(deslocamento),
      })
      if (busca) params.set('busca', busca)
      if (situacao) params.set('situacao', situacao)
      return ler<PaginaDeImportacoes>(`${BASE}?${params}`)
    },
    async enviar(arquivo) {
      const params = new URLSearchParams({ nome: arquivo.name })
      const resposta = await cliente.enviar<unknown>(`${BASE}?${params}`, {
        metodo: 'POST',
        arquivo,
        autenticada: true,
      })
      return converterChaves<ResumoDaImportacao>(resposta, CHAVES_OPACAS)
    },
    consultar: (id) => ler<DetalheDaImportacao>(`${BASE}/${id}`),
    definirColunas: (id, escolha: EscolhaDeColunas) =>
      mudar(`${BASE}/${id}/colunas`, 'PUT', {
        fonte: escolha.fonte,
        data_do_retrato: escolha.dataDoRetrato,
        mapeamento: escolha.mapeamento,
        valores_fixos: escolha.valoresFixos,
      }),
    responderPendencias: (id, respostas) =>
      mudar(`${BASE}/${id}/pendencias`, 'PUT', respostasEmJson(respostas)),
    confirmar: (id) => mudar(`${BASE}/${id}/confirmar`, 'POST'),
    cancelar: (id) => mudar(`${BASE}/${id}/cancelar`, 'POST'),
    desfazer: (id) => mudar(`${BASE}/${id}/desfazer`, 'POST'),
    registros: (id, deslocamento) => {
      const params = new URLSearchParams({
        limite: String(REGISTROS_POR_PAGINA),
        deslocamento: String(deslocamento),
      })
      return ler<PaginaDeRegistros>(`${BASE}/${id}/registros?${params}`)
    },
  }
}
