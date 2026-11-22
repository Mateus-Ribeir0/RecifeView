import { useMemo } from 'react'

import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'

const SEM_BAIRRO = 'Bairro não informado'

/** O nome oficial do bairro para exibir, a partir da chave que a base guarda. */
export function useNomeDoBairro(): (bairroOficial: string | null) => string {
  const { catalogo } = useCatalogoDoFormulario()
  return useMemo(() => {
    const nomes = new Map(catalogo?.bairros.map((bairro) => [bairro.chave, bairro.nome]))
    return (bairroOficial) =>
      bairroOficial ? (nomes.get(bairroOficial) ?? bairroOficial) : SEM_BAIRRO
  }, [catalogo])
}
