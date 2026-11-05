const QUANTIDADE_DE_CLASSES = 5

export interface FaixaDeClasse {
  inicio: number
  fim: number
}

function quantil(ordenados: readonly number[], posicao: number): number {
  const indice = posicao * (ordenados.length - 1)
  const abaixo = Math.floor(indice)
  const acima = Math.min(abaixo + 1, ordenados.length - 1)
  const inferior = ordenados[abaixo] ?? 0
  const superior = ordenados[acima] ?? inferior
  return inferior + (superior - inferior) * (indice - abaixo)
}

/** Cinco faixas com o mesmo número de bairros; limites repetidos juntam faixas vizinhas. */
export function faixasPorQuantis(valores: readonly number[]): FaixaDeClasse[] {
  const ordenados = [...valores].sort((a, b) => a - b)
  if (ordenados.length === 0) return []
  const cortes = Array.from({ length: QUANTIDADE_DE_CLASSES + 1 }, (_, indice) =>
    quantil(ordenados, indice / QUANTIDADE_DE_CLASSES),
  )
  const unicos = [...new Set(cortes)]
  if (unicos.length < 2) return [{ inicio: unicos[0] ?? 0, fim: unicos[0] ?? 0 }]
  return unicos.slice(1).map((fim, indice) => ({ inicio: unicos[indice] ?? 0, fim }))
}

export function faixasIguais(maximo: number): FaixaDeClasse[] {
  const largura = maximo / QUANTIDADE_DE_CLASSES
  return Array.from({ length: QUANTIDADE_DE_CLASSES }, (_, indice) => ({
    inicio: indice * largura,
    fim: (indice + 1) * largura,
  }))
}

export function classeDoValor(
  valor: number | null | undefined,
  faixas: readonly FaixaDeClasse[],
): number | null {
  if (valor === null || valor === undefined || faixas.length === 0) return null
  const posicao = faixas.findIndex((faixa) => valor <= faixa.fim)
  return (posicao === -1 ? faixas.length - 1 : posicao) + 1
}
