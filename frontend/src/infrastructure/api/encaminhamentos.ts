import type {
  ServicoDeEncaminhamentos,
  ServicoDeRetornoDoOrgao,
} from '../../application/encaminhamentos/servico'
import type {
  Encaminhamento,
  EncaminhamentoParaOOrgao,
  FiltroDeEncaminhamentos,
  OrgaoDoCatalogo,
  PreparoDoEncaminhamento,
  QuadroDeEncaminhamentos,
  RespostaAoEncaminhamento,
} from '../../domain/encaminhamentos'
import type { ClienteHttp, Requisicao } from './cliente'
import { converterChaves } from './conversao'

const BASE = '/encaminhamentos'
const ITENS_POR_PAGINA = 50

function paramsDoFiltro(filtro: FiltroDeEncaminhamentos): URLSearchParams {
  const params = new URLSearchParams({
    limite: String(ITENS_POR_PAGINA),
    deslocamento: String(filtro.deslocamento),
  })
  if (filtro.situacao) params.set('situacao', filtro.situacao)
  if (filtro.orgao) params.set('orgao', filtro.orgao)
  if (filtro.soAtrasados) params.set('so_atrasados', 'true')
  return params
}

function respostaEmJson(resposta: RespostaAoEncaminhamento) {
  return {
    situacao: resposta.situacao,
    protocolo_do_orgao: resposta.protocoloDoOrgao.trim() || null,
    observacao: resposta.observacao.trim() || null,
  }
}

export function criarServicoDeEncaminhamentos(cliente: ClienteHttp): ServicoDeEncaminhamentos {
  async function enviar<T>(caminho: string, requisicao: Requisicao = {}): Promise<T> {
    const resposta = await cliente.enviar<unknown>(caminho, { ...requisicao, autenticada: true })
    return converterChaves<T>(resposta)
  }

  return {
    orgaos: () => enviar<OrgaoDoCatalogo[]>(`${BASE}/orgaos`),
    preparar: (chave) =>
      enviar<PreparoDoEncaminhamento>(`${BASE}/ocorrencias/${encodeURIComponent(chave)}`),
    encaminhar: (pedido) =>
      enviar<Encaminhamento>(BASE, {
        metodo: 'POST',
        corpo: {
          chave_registro: pedido.chaveRegistro,
          orgao: pedido.orgao,
          justificativa: pedido.justificativa.trim() || null,
          nota: pedido.nota,
        },
      }),
    listar: (filtro) => enviar<QuadroDeEncaminhamentos>(`${BASE}?${paramsDoFiltro(filtro)}`),
    consultar: (id) => enviar<Encaminhamento>(`${BASE}/${id}`),
    registrarRetorno: (id, resposta) =>
      enviar<Encaminhamento>(`${BASE}/${id}/retorno`, {
        metodo: 'POST',
        corpo: respostaEmJson(resposta),
      }),
    reenviar: (id) => enviar<Encaminhamento>(`${BASE}/${id}/reenvio`, { metodo: 'POST' }),
  }
}

export function criarServicoDeRetornoDoOrgao(cliente: ClienteHttp): ServicoDeRetornoDoOrgao {
  async function postar(caminho: string, corpo: unknown): Promise<EncaminhamentoParaOOrgao> {
    const resposta = await cliente.enviar<unknown>(caminho, { metodo: 'POST', corpo })
    return converterChaves<EncaminhamentoParaOOrgao>(resposta)
  }

  return {
    abrir: (token) => postar('/retornos/abrir', { token }),
    responder: (token, resposta) => postar('/retornos', { token, ...respostaEmJson(resposta) }),
  }
}
