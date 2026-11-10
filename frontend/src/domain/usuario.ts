export type Perfil = 'GESTOR' | 'ADMINISTRADOR' | 'CIDADAO'
export type AreaDeAcesso = 'cidade' | 'gestao'

export interface Usuario {
  id: string
  nome: string
  email: string
  perfil: Perfil
  deveTrocarSenha: boolean
  bairroOficial: string | null
}

const ROTULOS_DE_PERFIL: Record<Perfil, string> = {
  GESTOR: 'Gestão pública',
  ADMINISTRADOR: 'Administração',
  CIDADAO: 'Cidadão',
}

export const ROTA_INICIAL_DA_GESTAO = '/painel'
export const ROTA_INICIAL_DA_CIDADE = '/cidade'

export function eDaGestao(perfil: Perfil): boolean {
  return perfil !== 'CIDADAO'
}

export function inicioDoPerfil(perfil: Perfil): string {
  return eDaGestao(perfil) ? ROTA_INICIAL_DA_GESTAO : ROTA_INICIAL_DA_CIDADE
}

export function podeAbrir(perfil: Perfil, caminho: string): boolean {
  return eDaGestao(perfil) || !caminho.startsWith(ROTA_INICIAL_DA_GESTAO)
}

const PALAVRAS_IGNORADAS_NAS_INICIAIS = new Set(['da', 'de', 'do', 'das', 'dos', 'e'])

export function rotuloDoPerfil(perfil: Perfil): string {
  return ROTULOS_DE_PERFIL[perfil]
}

export function iniciaisDoNome(nome: string): string {
  const palavras = nome
    .split(/\s+/)
    .filter((palavra) => palavra && !PALAVRAS_IGNORADAS_NAS_INICIAIS.has(palavra.toLowerCase()))
  const primeira = palavras.at(0)?.at(0) ?? ''
  const ultima = palavras.length > 1 ? (palavras.at(-1)?.at(0) ?? '') : ''
  return `${primeira}${ultima}`.toUpperCase()
}
