import { useId, useState, type ReactNode } from 'react'

import { useCatalogo } from '../../application/consultas/usePainel'
import { formatarNumero } from '../../domain/formatacao'
import { NOMES_CURTOS_DAS_FONTES, nomeDaFonte, type CodigoDaFonte } from '../../domain/fontes'
import { CORES_DAS_FONTES } from '../charts/estilo'
import estilos from './CabecalhoDaTela.module.css'
import { Icone } from './Icone'
import { useTituloDaPagina } from './useTituloDaPagina'

interface Propriedades {
  titulo: string
  children: ReactNode
  fontes?: readonly CodigoDaFonte[]
  notas?: readonly string[]
  atualizando?: boolean
  acoes?: ReactNode
}

function SeloDaFonte({ fonte, registros }: { fonte: CodigoDaFonte; registros?: number }) {
  const descricao =
    registros === undefined
      ? nomeDaFonte(fonte)
      : `${nomeDaFonte(fonte)}: ${formatarNumero(registros)} registros`
  return (
    <li className={estilos.fonte} title={descricao}>
      <span
        className={estilos.marca}
        style={{ background: CORES_DAS_FONTES[fonte] }}
        aria-hidden="true"
      />
      {NOMES_CURTOS_DAS_FONTES[fonte]}
    </li>
  )
}

export function CabecalhoDaTela({
  titulo,
  children,
  fontes = [],
  notas = [],
  atualizando,
  acoes,
}: Propriedades) {
  useTituloDaPagina(titulo)
  const [notasAbertas, definirNotasAbertas] = useState(false)
  const idDasNotas = useId()
  const { dados: catalogo } = useCatalogo()
  const registros = new Map(catalogo?.fontes.map((fonte) => [fonte.codigo, fonte.registros]))

  return (
    <header className={estilos.cabecalho}>
      <div className={estilos.topo}>
        <div className={estilos.textos}>
          <h1 className={estilos.titulo}>{titulo}</h1>
          <p className={estilos.pergunta}>{children}</p>
        </div>
        {acoes && <div className={estilos.acoes}>{acoes}</div>}
      </div>
      {(fontes.length > 0 || notas.length > 0) && (
        <div className={estilos.apoio}>
          {fontes.length > 0 && (
            <ul className={estilos.fontes} aria-label="Fontes desta tela">
              {fontes.map((fonte) => (
                <SeloDaFonte key={fonte} fonte={fonte} registros={registros.get(fonte)} />
              ))}
            </ul>
          )}
          {notas.length > 0 && (
            <button
              type="button"
              className={estilos.sobre}
              aria-expanded={notasAbertas}
              aria-controls={idDasNotas}
              onClick={() => definirNotasAbertas((atual) => !atual)}
            >
              <Icone nome="informacao" tamanho={16} />
              Sobre esta tela
            </button>
          )}
          {atualizando && (
            <span className={estilos.atualizando} role="status">
              Atualizando
            </span>
          )}
        </div>
      )}
      {notasAbertas && (
        <ul id={idDasNotas} className={estilos.notas}>
          {notas.map((nota) => (
            <li key={nota}>{nota}</li>
          ))}
        </ul>
      )}
    </header>
  )
}
