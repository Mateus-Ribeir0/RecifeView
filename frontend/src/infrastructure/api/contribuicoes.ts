import type { ServicoDeContribuicoes } from '../../application/contribuicoes/servico'
import type {
  CatalogoDoFormulario,
  PaginaDeOcorrencias,
  ParParaRevisar,
  ResultadoDoEnvio,
  ResumoDasContribuicoes,
} from '../../domain/contribuicoes'
import type { ResumoDaImportacao } from '../../domain/importacoes'
import type { ClienteHttp } from './cliente'
import { converterChaves } from './conversao'

const BASE = '/contribuicoes'
const OCORRENCIAS_POR_PAGINA = 50
const CHAVES_OPACAS: ReadonlySet<string> = new Set(['descartes', 'correcoes', 'fontes', 'detalhes'])

export function criarServicoDeContribuicoes(cliente: ClienteHttp): ServicoDeContribuicoes {
  async function lerPublico<T>(caminho: string): Promise<T> {
    return converterChaves<T>(await cliente.enviar<unknown>(caminho))
  }

  async function lerDaGestao<T>(caminho: string): Promise<T> {
    return converterChaves<T>(await cliente.enviar<unknown>(caminho, { autenticada: true }))
  }

  return {
    catalogo: () => lerPublico<CatalogoDoFormulario>(`${BASE}/catalogo`),
    logradouros: (bairro) => {
      const params = new URLSearchParams({ bairro })
      return lerPublico<string[]>(`${BASE}/logradouros?${params}`)
    },
    async enviar(relato) {
      const resposta = await cliente.enviar<{ resultado: ResultadoDoEnvio }>(BASE, {
        metodo: 'POST',
        corpo: {
          chave_de_envio: relato.chaveDeEnvio,
          servico_codigo: relato.servicoCodigo,
          bairro_oficial: relato.bairroOficial,
          logradouro: relato.logradouro,
          numero: relato.numero,
          detalhe: relato.detalhe,
          retorno: relato.retorno,
          site: relato.site,
        },
      })
      return resposta.resultado
    },
    resumo: () => lerDaGestao<ResumoDasContribuicoes>(`${BASE}/resumo`),
    ocorrencias: (deslocamento) => {
      const params = new URLSearchParams({
        limite: String(OCORRENCIAS_POR_PAGINA),
        deslocamento: String(deslocamento),
      })
      return lerDaGestao<PaginaDeOcorrencias>(`${BASE}/ocorrencias?${params}`)
    },
    pares: () => lerDaGestao<ParParaRevisar[]>(`${BASE}/pares`),
    async decidir(parId, decisao) {
      await cliente.enviar<unknown>(`${BASE}/pares/${parId}`, {
        metodo: 'PUT',
        corpo: { decisao },
        autenticada: true,
      })
    },
    async gerarPacote() {
      const resposta = await cliente.enviar<unknown>(`${BASE}/pacotes`, {
        metodo: 'POST',
        autenticada: true,
      })
      return converterChaves<ResumoDaImportacao>(resposta, CHAVES_OPACAS)
    },
  }
}
