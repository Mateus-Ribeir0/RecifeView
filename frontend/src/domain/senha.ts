export const TAMANHO_MINIMO_DA_SENHA = 12
const TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO = 4

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
      descricao: 'Diferente da senha atual',
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
