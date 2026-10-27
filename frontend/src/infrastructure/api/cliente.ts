import {
  ErroDoRecifeView,
  MENSAGEM_DE_SERVICO_INDISPONIVEL,
  type CodigoDeErro,
} from '../../domain/erros'

const STATUS_NAO_AUTORIZADO = 401
const STATUS_SEM_CONTEUDO = 204
const STATUS_DE_ERRO_DO_SERVIDOR = 500
const MENSAGEM_PADRAO = 'Não foi possível concluir a operação. Tente de novo.'

const CODIGOS_CONHECIDOS: ReadonlySet<string> = new Set<CodigoDeErro>([
  'credenciais_invalidas',
  'conta_bloqueada',
  'conta_inativa',
  'sessao_invalida',
  'senha_atual_incorreta',
  'senha_fraca',
  'dados_invalidos',
])

export interface Requisicao {
  metodo?: 'GET' | 'POST'
  corpo?: unknown
  autenticada?: boolean
}

interface CorpoDeErro {
  erro?: { codigo?: string; mensagem?: string; detalhes?: { desbloqueio_em?: string } }
}

type Buscar = typeof fetch
type Renovador = () => Promise<boolean>

export class ClienteHttp {
  private readonly urlBase: string
  private readonly buscar: Buscar
  private readonly ouvintesDePerda = new Set<() => void>()
  private tokenDeAcesso: string | null = null
  private renovador: Renovador | null = null
  private renovacaoEmCurso: Promise<boolean> | null = null

  constructor(urlBase: string, buscar: Buscar = (...argumentos) => fetch(...argumentos)) {
    this.urlBase = urlBase
    this.buscar = buscar
  }

  definirTokenDeAcesso(token: string | null): void {
    this.tokenDeAcesso = token
  }

  definirRenovador(renovador: Renovador): void {
    this.renovador = renovador
  }

  observarPerdaDeSessao(ouvinte: () => void): () => void {
    this.ouvintesDePerda.add(ouvinte)
    return () => this.ouvintesDePerda.delete(ouvinte)
  }

  async enviar<T>(caminho: string, requisicao: Requisicao = {}): Promise<T> {
    const resposta = await this.executar(caminho, requisicao)
    if (resposta.status !== STATUS_NAO_AUTORIZADO || !requisicao.autenticada) {
      return this.ler<T>(resposta)
    }
    if (await this.renovarUmaVez()) {
      return this.ler<T>(await this.executar(caminho, requisicao))
    }
    this.ouvintesDePerda.forEach((ouvinte) => ouvinte())
    return this.ler<T>(resposta)
  }

  private async executar(caminho: string, requisicao: Requisicao): Promise<Response> {
    const cabecalhos = new Headers({ Accept: 'application/json' })
    if (requisicao.corpo !== undefined) cabecalhos.set('Content-Type', 'application/json')
    if (requisicao.autenticada && this.tokenDeAcesso) {
      cabecalhos.set('Authorization', `Bearer ${this.tokenDeAcesso}`)
    }
    try {
      return await this.buscar(`${this.urlBase}${caminho}`, {
        method: requisicao.metodo ?? 'GET',
        headers: cabecalhos,
        body: requisicao.corpo === undefined ? undefined : JSON.stringify(requisicao.corpo),
        credentials: 'include',
      })
    } catch {
      throw new ErroDoRecifeView('servico_indisponivel', MENSAGEM_DE_SERVICO_INDISPONIVEL)
    }
  }

  private renovarUmaVez(): Promise<boolean> {
    if (!this.renovador) return Promise.resolve(false)
    this.renovacaoEmCurso ??= this.renovador().finally(() => {
      this.renovacaoEmCurso = null
    })
    return this.renovacaoEmCurso
  }

  private async ler<T>(resposta: Response): Promise<T> {
    if (resposta.status === STATUS_SEM_CONTEUDO) return undefined as T
    const corpo: unknown = await resposta.json().catch(() => null)
    if (resposta.ok) return corpo as T
    throw converterErro(resposta.status, corpo as CorpoDeErro | null)
  }
}

function converterErro(status: number, corpo: CorpoDeErro | null): ErroDoRecifeView {
  const erro = corpo?.erro
  if (erro?.codigo && CODIGOS_CONHECIDOS.has(erro.codigo)) {
    const desbloqueio = erro.detalhes?.desbloqueio_em
    return new ErroDoRecifeView(
      erro.codigo as CodigoDeErro,
      erro.mensagem ?? MENSAGEM_PADRAO,
      desbloqueio ? new Date(desbloqueio) : null,
    )
  }
  if (status >= STATUS_DE_ERRO_DO_SERVIDOR) {
    return new ErroDoRecifeView('servico_indisponivel', MENSAGEM_DE_SERVICO_INDISPONIVEL)
  }
  return new ErroDoRecifeView('erro_inesperado', erro?.mensagem ?? MENSAGEM_PADRAO)
}
