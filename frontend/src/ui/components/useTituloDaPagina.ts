import { useEffect } from 'react'

const NOME_DO_PRODUTO = 'RecifeView'

export function useTituloDaPagina(titulo: string | null): void {
  useEffect(() => {
    document.title = titulo ? `${titulo} · ${NOME_DO_PRODUTO}` : NOME_DO_PRODUTO
  }, [titulo])
}
