export type CodigoDeErro =
  | 'credenciais_invalidas'
  | 'conta_bloqueada'
  | 'conta_inativa'
  | 'sessao_invalida'
  | 'senha_atual_incorreta'
  | 'senha_fraca'
  | 'dados_invalidos'
  | 'contribuicao_invalida'
  | 'area_da_gestao_negada'
  | 'acesso_negado'
  | 'codigo_invalido'
  | 'cadastro_invalido'
  | 'tentativas_demais'
  | 'envio_de_email_indisponivel'
  | 'protocolo_invalido'
  | 'limite_de_pedidos'
  | 'encaminhamento_invalido'
  | 'ocorrencia_ja_encaminhada'
  | 'resposta_fora_de_ordem'
  | 'link_de_retorno_invalido'
  | 'origem_recusada'
  | 'origem_indisponivel'
  | 'servico_indisponivel'
  | 'erro_inesperado'

export class ErroDoRecifeView extends Error {
  readonly codigo: CodigoDeErro
  readonly desbloqueioEm: Date | null
  readonly campo: string | null

  constructor(
    codigo: CodigoDeErro,
    mensagem: string,
    desbloqueioEm: Date | null = null,
    campo: string | null = null,
  ) {
    super(mensagem)
    this.name = 'ErroDoRecifeView'
    this.codigo = codigo
    this.desbloqueioEm = desbloqueioEm
    this.campo = campo
  }
}

export const MENSAGEM_DE_SERVICO_INDISPONIVEL =
  'Não foi possível falar com o servidor do RecifeView. Confira sua conexão e tente de novo.'
