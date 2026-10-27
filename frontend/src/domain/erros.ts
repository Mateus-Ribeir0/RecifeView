export type CodigoDeErro =
  | 'credenciais_invalidas'
  | 'conta_bloqueada'
  | 'conta_inativa'
  | 'sessao_invalida'
  | 'senha_atual_incorreta'
  | 'senha_fraca'
  | 'dados_invalidos'
  | 'servico_indisponivel'
  | 'erro_inesperado'

export class ErroDoRecifeView extends Error {
  readonly codigo: CodigoDeErro
  readonly desbloqueioEm: Date | null

  constructor(codigo: CodigoDeErro, mensagem: string, desbloqueioEm: Date | null = null) {
    super(mensagem)
    this.name = 'ErroDoRecifeView'
    this.codigo = codigo
    this.desbloqueioEm = desbloqueioEm
  }
}

export const MENSAGEM_DE_SERVICO_INDISPONIVEL =
  'Não foi possível falar com o servidor do RecifeView. Confira sua conexão e tente de novo.'
