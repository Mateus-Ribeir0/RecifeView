import type { RequisitoDaSenha } from './senha'
import { TAMANHO_MINIMO_DA_SENHA } from './senha'

export const DIGITOS_DO_CODIGO = 6
export const TAMANHO_MAXIMO_DO_NOME = 80
const TAMANHO_MINIMO_DO_NOME = 2
const TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO = 4
const DISTANCIA_MAXIMA_DA_SUGESTAO = 2
const FORMATO_DE_EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/
const FORA_DO_NOME = /[^\p{L}' -]/gu
const ESPACOS_REPETIDOS = / {2,}/g
const NOME_COMPLETO = /^\p{L}+(?:[ '-]\p{L}+)*$/u

// Domínios mais comuns no Brasil: um erro de digitação aqui faz o código nunca chegar.
const DOMINIOS_CONHECIDOS = [
  'gmail.com',
  'hotmail.com',
  'outlook.com',
  'yahoo.com.br',
  'yahoo.com',
  'icloud.com',
  'live.com',
  'uol.com.br',
  'bol.com.br',
  'terra.com.br',
  'recife.pe.gov.br',
]

export type CampoDoCadastro = 'nome' | 'email' | 'senha' | 'confirmacao' | 'termos' | 'bairro'
export type ErrosDoCadastro = Partial<Record<CampoDoCadastro, string>>

export interface DadosDoCadastro {
  nome: string
  email: string
  senha: string
  confirmacao: string
  aceitouOsTermos: boolean
}

export function normalizarEmail(texto: string): string {
  return texto.trim().toLowerCase()
}

export function emailValido(texto: string): boolean {
  return FORMATO_DE_EMAIL.test(normalizarEmail(texto))
}

function distancia(a: string, b: string): number {
  let anterior = Array.from({ length: b.length + 1 }, (_, indice) => indice)
  for (let i = 1; i <= a.length; i += 1) {
    const atual = [i]
    for (let j = 1; j <= b.length; j += 1) {
      const troca = a[i - 1] === b[j - 1] ? 0 : 1
      atual[j] = Math.min(
        (anterior[j] ?? 0) + 1,
        (atual[j - 1] ?? 0) + 1,
        (anterior[j - 1] ?? 0) + troca,
      )
    }
    anterior = atual
  }
  return anterior[b.length] ?? 0
}

export function sugerirEmail(texto: string): string | null {
  const email = normalizarEmail(texto)
  if (!emailValido(email)) return null
  const [usuario = '', dominio = ''] = email.split('@')
  if (DOMINIOS_CONHECIDOS.includes(dominio)) return null
  const proximo = DOMINIOS_CONHECIDOS.find(
    (conhecido) => distancia(dominio, conhecido) <= DISTANCIA_MAXIMA_DA_SUGESTAO,
  )
  return proximo ? `${usuario}@${proximo}` : null
}

export function mascararNome(texto: string): string {
  return texto.replace(FORA_DO_NOME, '').replace(ESPACOS_REPETIDOS, ' ').trimStart()
}

export function validarNome(texto: string): string | null {
  const nome = texto.trim()
  if (nome.length < TAMANHO_MINIMO_DO_NOME) return 'Informe o seu nome.'
  if (nome.length > TAMANHO_MAXIMO_DO_NOME) return 'Use até 80 caracteres.'
  if (!NOME_COMPLETO.test(nome)) return 'Use só letras, espaço, hífen ou apóstrofo.'
  return null
}

export function digitosDoCodigo(texto: string): string {
  return texto.replace(/\D/g, '').slice(0, DIGITOS_DO_CODIGO)
}

export function mascararCodigo(texto: string): string {
  const digitos = digitosDoCodigo(texto)
  return digitos.length > 3 ? `${digitos.slice(0, 3)} ${digitos.slice(3)}` : digitos
}

export function codigoCompleto(texto: string): boolean {
  return digitosDoCodigo(texto).length === DIGITOS_DO_CODIGO
}

function contemNomeDeUsuario(senha: string, email: string): boolean {
  const nome = normalizarEmail(email).split('@')[0] ?? ''
  return (
    nome.length >= TAMANHO_MINIMO_DO_NOME_DE_USUARIO_COMPARADO && senha.toLowerCase().includes(nome)
  )
}

export function avaliarSenhaDoCadastro(
  dados: Pick<DadosDoCadastro, 'senha' | 'confirmacao' | 'email'>,
): RequisitoDaSenha[] {
  const { senha, confirmacao, email } = dados
  return [
    {
      descricao: `Pelo menos ${TAMANHO_MINIMO_DA_SENHA} caracteres`,
      atendido: senha.length >= TAMANHO_MINIMO_DA_SENHA && new Set(senha).size > 1,
    },
    {
      descricao: 'Sem a parte do seu e-mail antes do @',
      atendido: senha.length > 0 && !contemNomeDeUsuario(senha, email),
    },
    {
      descricao: 'As duas senhas conferem',
      atendido: senha.length > 0 && senha === confirmacao,
    },
  ]
}

export function errosDoCadastro(dados: DadosDoCadastro): ErrosDoCadastro {
  const erros: ErrosDoCadastro = {}
  const erroDoNome = validarNome(dados.nome)
  if (erroDoNome) erros.nome = erroDoNome
  if (!emailValido(dados.email)) erros.email = 'Informe um e-mail válido, como nome@exemplo.com.'
  const [tamanho, semEmail, conferem] = avaliarSenhaDoCadastro(dados)
  if (!tamanho?.atendido || !semEmail?.atendido) {
    erros.senha = 'A senha ainda não atende às regras abaixo.'
  }
  if (dados.senha && !conferem?.atendido) erros.confirmacao = 'As senhas não conferem.'
  if (!dados.aceitouOsTermos) erros.termos = 'Para criar a conta, aceite como usamos os seus dados.'
  return erros
}
