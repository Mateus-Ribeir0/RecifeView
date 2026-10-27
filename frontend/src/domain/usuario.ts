export type Perfil = 'GESTOR' | 'ADMINISTRADOR'

export interface Usuario {
  id: string
  nome: string
  email: string
  perfil: Perfil
  deveTrocarSenha: boolean
}

const ROTULOS_DE_PERFIL: Record<Perfil, string> = {
  GESTOR: 'Gestão pública',
  ADMINISTRADOR: 'Administração',
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
