type Json = unknown

function paraCamelCase(chave: string): string {
  return chave.replace(/_([a-z0-9])/g, (_, letra: string) => letra.toUpperCase())
}

/** Converte as chaves do JSON da API. Dicionários de dados (nomes de coluna) ficam como vieram. */
export function converterChaves<T>(valor: Json, chavesOpacas: ReadonlySet<string> = new Set()): T {
  if (Array.isArray(valor)) {
    return valor.map((item) => converterChaves(item, chavesOpacas)) as T
  }
  if (typeof valor !== 'object' || valor === null) return valor as T
  const convertido: Record<string, Json> = {}
  for (const [chave, item] of Object.entries(valor)) {
    convertido[paraCamelCase(chave)] = chavesOpacas.has(chave)
      ? item
      : converterChaves(item, chavesOpacas)
  }
  return convertido as T
}
