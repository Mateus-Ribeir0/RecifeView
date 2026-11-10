import { pareceEmail } from '../../../domain/acesso'

export interface ErrosDaEntrada {
  email?: string
  senha?: string
}

function validarEmail(email: string): string | undefined {
  if (!email.trim()) return 'Informe o seu e-mail.'
  if (!pareceEmail(email)) return 'Informe um e-mail válido, como nome@exemplo.com.'
  return undefined
}

export function validarEntrada(email: string, senha: string): ErrosDaEntrada {
  return {
    email: validarEmail(email),
    senha: senha ? undefined : 'Informe a sua senha.',
  }
}
