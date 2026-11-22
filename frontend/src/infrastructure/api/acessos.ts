import type { ServicoDeAcessos } from '../../application/acessos/servico'
import type { AcessoCorporativo, DadosDoAcesso, ListaDeAcessos } from '../../domain/acessos'
import type { ClienteHttp, Requisicao } from './cliente'
import { converterChaves } from './conversao'

const BASE = '/acessos-corporativos'

function dadosEmJson(dados: DadosDoAcesso) {
  return { nome: dados.nome.trim(), orgao: dados.orgao }
}

export function criarServicoDeAcessos(cliente: ClienteHttp): ServicoDeAcessos {
  async function enviar<T>(caminho: string, requisicao: Requisicao = {}): Promise<T> {
    const resposta = await cliente.enviar<unknown>(caminho, { ...requisicao, autenticada: true })
    return converterChaves<T>(resposta)
  }
  const acao = (id: string, caminho: string) =>
    enviar<AcessoCorporativo>(`${BASE}/${encodeURIComponent(id)}/${caminho}`, { metodo: 'POST' })

  return {
    listar: () => enviar<ListaDeAcessos>(BASE),
    criar: (novo) =>
      enviar<AcessoCorporativo>(BASE, {
        metodo: 'POST',
        corpo: { ...dadosEmJson(novo), email: novo.email.trim() },
      }),
    editar: (id, dados) =>
      enviar<AcessoCorporativo>(`${BASE}/${encodeURIComponent(id)}`, {
        metodo: 'PUT',
        corpo: dadosEmJson(dados),
      }),
    reenviarConvite: (id) => acao(id, 'convite'),
    desativar: (id) => acao(id, 'desativacao'),
    reativar: (id) => acao(id, 'reativacao'),
    excluir: async (id) => {
      await cliente.enviar<unknown>(`${BASE}/${encodeURIComponent(id)}`, {
        metodo: 'DELETE',
        autenticada: true,
      })
    },
  }
}
