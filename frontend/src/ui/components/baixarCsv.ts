const SEPARADOR = ';'
const MARCA_DE_UTF8 = String.fromCharCode(0xfeff)

function celula(valor: string | number): string {
  return `"${String(valor).replace(/"/g, '""')}"`
}

export function baixarCsv(
  nomeDoArquivo: string,
  cabecalho: readonly string[],
  linhas: readonly (readonly (string | number)[])[],
): void {
  const conteudo = [cabecalho, ...linhas]
    .map((linha) => linha.map(celula).join(SEPARADOR))
    .join('\n')
  const endereco = URL.createObjectURL(
    new Blob([`${MARCA_DE_UTF8}${conteudo}`], { type: 'text/csv' }),
  )
  const link = document.createElement('a')
  link.href = endereco
  link.download = nomeDoArquivo
  link.click()
  URL.revokeObjectURL(endereco)
}
