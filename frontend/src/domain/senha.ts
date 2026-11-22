export const TAMANHO_MINIMO_DA_SENHA = 12
const TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO = 4
const DIFERENTE_DA_ATUAL = 'Diferente da senha atual'

export interface DadosDaNovaSenha {
  novaSenha: string
  confirmacao: string
  senhaAtual: string
  email: string
}

export interface RequisitoDaSenha {
  descricao: string
  atendido: boolean
}

function contemNomeDeUsuario(senha: string, email: string): boolean {
  const nome = email.split('@')[0]?.toLowerCase() ?? ''
  return (
    nome.length >= TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO && senha.toLowerCase().includes(nome)
  )
}

export function avaliarNovaSenha(dados: DadosDaNovaSenha): RequisitoDaSenha[] {
  const { novaSenha, confirmacao, senhaAtual, email } = dados
  return [
    {
      descricao: `Pelo menos ${TAMANHO_MINIMO_DA_SENHA} caracteres`,
      atendido: novaSenha.length >= TAMANHO_MINIMO_DA_SENHA && new Set(novaSenha).size > 1,
    },
    {
      descricao: DIFERENTE_DA_ATUAL,
      atendido: novaSenha.length > 0 && novaSenha !== senhaAtual,
    },
    {
      descricao: 'Sem a parte do seu e-mail antes do @',
      atendido: novaSenha.length > 0 && !contemNomeDeUsuario(novaSenha, email),
    },
    {
      descricao: 'As duas senhas conferem',
      atendido: novaSenha.length > 0 && novaSenha === confirmacao,
    },
  ]
}

export function novaSenhaEstaValida(dados: DadosDaNovaSenha): boolean {
  return avaliarNovaSenha(dados).every((requisito) => requisito.atendido)
}

export type DadosDaPrimeiraSenha = Omit<DadosDaNovaSenha, 'senhaAtual'>

/** No convite ainda não existe senha atual: a regra de ser diferente dela não se aplica. */
export function avaliarPrimeiraSenha(dados: DadosDaPrimeiraSenha): RequisitoDaSenha[] {
  return avaliarNovaSenha({ ...dados, senhaAtual: '' }).filter(
    (requisito) => requisito.descricao !== DIFERENTE_DA_ATUAL,
  )
}
