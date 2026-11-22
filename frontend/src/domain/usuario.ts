import type { Orgao } from './encaminhamentos'

export type Perfil = 'GESTOR' | 'ADMINISTRADOR' | 'CIDADAO' | 'CORPORATIVO'
export type AreaDeAcesso = 'cidade' | 'gestao' | 'corporativo'

export interface Usuario {
  id: string
  nome: string
  email: string
  perfil: Perfil
  deveTrocarSenha: boolean
  bairroOficial: string | null
  recebeAvisos: boolean
  orgao: Orgao | null
  nomeDoOrgao: string | null
}

const ROTULOS_DE_PERFIL: Record<Perfil, string> = {
  GESTOR: 'Gestão pública',
  ADMINISTRADOR: 'Administração',
  CIDADAO: 'Cidadão',
  CORPORATIVO: 'Acesso corporativo',
}

export const ROTA_INICIAL_DA_GESTAO = '/painel'
export const ROTA_INICIAL_DA_CIDADE = '/cidade'
export const ROTA_INICIAL_CORPORATIVA = '/corporativo'

const INICIO_POR_PERFIL: Readonly<Record<Perfil, string>> = {
  GESTOR: ROTA_INICIAL_DA_GESTAO,
  ADMINISTRADOR: ROTA_INICIAL_DA_GESTAO,
  CIDADAO: ROTA_INICIAL_DA_CIDADE,
  CORPORATIVO: ROTA_INICIAL_CORPORATIVA,
}
const AREAS_RESTRITAS = [ROTA_INICIAL_DA_GESTAO, ROTA_INICIAL_DA_CIDADE, ROTA_INICIAL_CORPORATIVA]

export function eDaGestao(perfil: Perfil): boolean {
  return perfil === 'GESTOR' || perfil === 'ADMINISTRADOR'
}

export function eDaAdministracao(perfil: Perfil): boolean {
  return perfil === 'ADMINISTRADOR'
}

export function eCorporativo(perfil: Perfil): boolean {
  return perfil === 'CORPORATIVO'
}

export function inicioDoPerfil(perfil: Perfil): string {
  return INICIO_POR_PERFIL[perfil]
}

/** Cada perfil abre só a sua área: as rotas restritas dos outros perfis ficam de fora. */
export function podeAbrir(perfil: Perfil, caminho: string): boolean {
  const propria = inicioDoPerfil(perfil)
  return !AREAS_RESTRITAS.some((area) => area !== propria && caminho.startsWith(area))
}

const PALAVRAS_IGNORADAS_NAS_INICIAIS = new Set(['da', 'de', 'do', 'das', 'dos', 'e'])

export function rotuloDoPerfil(perfil: Perfil): string {
  return ROTULOS_DE_PERFIL[perfil]
}

export function rotuloDaConta(usuario: Usuario): string {
  return usuario.nomeDoOrgao ?? rotuloDoPerfil(usuario.perfil)
}

export function iniciaisDoNome(nome: string): string {
  const palavras = nome
    .split(/\s+/)
    .filter((palavra) => palavra && !PALAVRAS_IGNORADAS_NAS_INICIAIS.has(palavra.toLowerCase()))
  const primeira = palavras.at(0)?.at(0) ?? ''
  const ultima = palavras.length > 1 ? (palavras.at(-1)?.at(0) ?? '') : ''
  return `${primeira}${ultima}`.toUpperCase()
}
