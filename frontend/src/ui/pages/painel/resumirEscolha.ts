export interface OpcaoDoSeletor {
  valor: string
  rotulo: string
}

export function resumirEscolha(
  selecionados: readonly string[],
  opcoes: readonly OpcaoDoSeletor[],
  nenhum: string,
): string {
  const [primeiro] = selecionados
  if (primeiro === undefined) return nenhum
  if (selecionados.length > 1) return `${selecionados.length} escolhidos`
  return opcoes.find((opcao) => opcao.valor === primeiro)?.rotulo ?? primeiro
}
