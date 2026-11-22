import type { ServicoDoOrgao } from '../../application/corporativo/servico'
import type {
  DemandaDoOrgao,
  FilaDoOrgao,
  OcorrenciaDoOrgao,
  PainelDoOrgao,
  PedidoDaFila,
  RespostaComoOrgao,
  RespostaRegistrada,
} from '../../domain/corporativo'
import type { ClienteHttp, Requisicao } from './cliente'
import { converterChaves } from './conversao'

const BASE = '/corporativo'
const CHAVES_DAS_ABAS = new Set(['por_aba'])

function paramsDaFila(pedido: PedidoDaFila): URLSearchParams {
  const params = new URLSearchParams({ aba: pedido.aba, deslocamento: String(pedido.deslocamento) })
  if (pedido.bairro) params.set('bairro', pedido.bairro)
  if (pedido.categoria) params.set('categoria', pedido.categoria)
  return params
}

function respostaEmJson(resposta: RespostaComoOrgao) {
  return {
    situacao: resposta.situacao,
    resposta_ao_cidadao: resposta.respostaAoCidadao.trim() || null,
    observacao: resposta.observacao.trim() || null,
    protocolo_do_orgao: resposta.protocoloDoOrgao.trim() || null,
    previsao: resposta.situacao === 'recebido' ? resposta.previsao : null,
    tambem: resposta.tambem,
  }
}

export function criarServicoDoOrgao(cliente: ClienteHttp): ServicoDoOrgao {
  async function enviar<T>(
    caminho: string,
    requisicao: Requisicao = {},
    chavesOpacas: ReadonlySet<string> = new Set(),
  ): Promise<T> {
    const resposta = await cliente.enviar<unknown>(caminho, { ...requisicao, autenticada: true })
    return converterChaves<T>(resposta, chavesOpacas)
  }

  return {
    painel: () => enviar<PainelDoOrgao>(`${BASE}/painel`),
    fila: (pedido) =>
      enviar<FilaDoOrgao>(`${BASE}/ocorrencias?${paramsDaFila(pedido)}`, {}, CHAVES_DAS_ABAS),
    ocorrencia: (id) => enviar<OcorrenciaDoOrgao>(`${BASE}/ocorrencias/${id}`),
    responder: (id, resposta) =>
      enviar<RespostaRegistrada>(`${BASE}/ocorrencias/${id}/resposta`, {
        metodo: 'POST',
        corpo: respostaEmJson(resposta),
      }),
    dados: ({ anoInicio, anoFim }) =>
      enviar<DemandaDoOrgao>(`${BASE}/dados?ano_inicio=${anoInicio}&ano_fim=${anoFim}`),
  }
}
