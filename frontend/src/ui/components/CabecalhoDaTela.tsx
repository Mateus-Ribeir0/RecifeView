import type { ReactNode } from 'react'

import { useCatalogo } from '../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../application/filtros/contexto'
import { resumirRecorte } from '../../domain/filtros'
import { formatarNumero } from '../../domain/formatacao'
import { nomeDaFonte } from '../../domain/fontes'
import estilos from './CabecalhoDaTela.module.css'
import { useTituloDaPagina } from './useTituloDaPagina'

interface Propriedades {
  titulo: string
  children: ReactNode
  fontes?: readonly string[]
  ignorados?: readonly string[]
  atualizando?: boolean
  semRecorte?: boolean
}

export function CabecalhoDaTela({
  titulo,
  children,
  fontes,
  ignorados,
  atualizando,
  semRecorte,
}: Propriedades) {
  useTituloDaPagina(titulo)
  const { filtros } = useFiltrosGlobais()
  const { dados: catalogo } = useCatalogo()
  const nomes = new Map(catalogo?.bairros.map((bairro) => [bairro.bairroOficial, bairro.nome]))
  const registros = new Map(catalogo?.fontes.map((fonte) => [fonte.codigo, fonte.registros]))
  const rotuloDaFonte = (codigo: string) => {
    const total = registros.get(codigo)
    const nome = nomeDaFonte(codigo)
    return total === undefined ? nome : `${nome} (${formatarNumero(total)} registros)`
  }

  return (
    <header className={estilos.cabecalho}>
      <h1 className={estilos.titulo}>{titulo}</h1>
      <p className={estilos.pergunta}>{children}</p>
      {!semRecorte && (
        <p className={estilos.recorte} aria-live="polite">
          Recorte: {resumirRecorte(filtros, (bairro) => nomes.get(bairro) ?? bairro)}
          {atualizando && <span className={estilos.atualizando}> · atualizando...</span>}
        </p>
      )}
      {ignorados?.map((texto) => (
        <p key={texto} className={estilos.recorte}>
          {texto}
        </p>
      ))}
      {fontes && (
        <p className={estilos.recorte}>
          Fontes nesta tela: {fontes.map(rotuloDaFonte).join(' · ')}.
        </p>
      )}
    </header>
  )
}
