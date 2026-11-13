import { NavLink, useLocation } from 'react-router'

import { useCatalogo } from '../../../application/consultas/usePainel'
import { usePendenciasDoPainel } from '../../../application/encaminhamentos/useEncaminhamentos'
import type { PendenciasDoPainel } from '../../../domain/encaminhamentos'
import { contar, formatarNumero } from '../../../domain/formatacao'
import { Icone } from '../../components/Icone'
import {
  GRUPOS_DE_TELAS,
  ROTA_RAIZ_DO_PAINEL,
  type PendenciaDaTela,
} from '../../conteudo/telasDoPainel'
import estilos from './BarraLateral.module.css'

function contarPendencias(pendencias: PendenciasDoPainel, tela: PendenciaDaTela): number {
  return tela === 'encaminhamentos' ? pendencias.pedemAcao : pendencias.duplasNoPenteFino
}

const DESCRICAO_DA_PENDENCIA: Readonly<Record<PendenciaDaTela, [string, string]>> = {
  encaminhamentos: ['encaminhamento pede ação', 'encaminhamentos pedem ação'],
  contribuicoes: ['dupla espera o pente fino', 'duplas esperam o pente fino'],
}

function Contador({ quantidade, tela }: { quantidade: number; tela: PendenciaDaTela }) {
  if (quantidade === 0) return null
  const [singular, plural] = DESCRICAO_DA_PENDENCIA[tela]
  return (
    <span className={`${estilos.contador} numero`} title={contar(quantidade, singular, plural)}>
      {formatarNumero(quantidade)}
      <span className="visualmente-oculto">{`, ${contar(quantidade, singular, plural)}`}</span>
    </span>
  )
}

interface Propriedades {
  recolhida: boolean
  aoNavegar: () => void
}

function ResumoDaBase() {
  const { dados: catalogo } = useCatalogo()
  if (!catalogo) return null
  const registros = catalogo.fontes.reduce((soma, fonte) => soma + fonte.registros, 0)
  return (
    <p className={estilos.resumo}>
      <strong className="numero">{formatarNumero(registros)}</strong> registros de{' '}
      {catalogo.fontes.length} fontes, {catalogo.anoMinimo} a {catalogo.anoMaximo}
    </p>
  )
}

export function BarraLateral({ recolhida, aoNavegar }: Propriedades) {
  const { pathname } = useLocation()
  const { dados: pendencias } = usePendenciasDoPainel(pathname)
  return (
    <nav
      aria-label="Telas do painel"
      className={`${estilos.lateral} ${recolhida ? estilos.recolhida : ''}`}
    >
      {GRUPOS_DE_TELAS.map(({ grupo, telas }) => (
        <div key={grupo} className={estilos.bloco}>
          <p className={estilos.grupo}>{grupo}</p>
          <ul>
            {telas.map((tela) => (
              <li key={tela.caminho}>
                <NavLink
                  to={tela.caminho}
                  end={tela.caminho === ROTA_RAIZ_DO_PAINEL}
                  className={estilos.item}
                  title={recolhida ? undefined : tela.mostra}
                  data-rotulo={tela.nome}
                  onClick={aoNavegar}
                >
                  <Icone nome={tela.icone} />
                  <span className={estilos.nome}>{tela.nome}</span>
                  {pendencias && tela.pendencia && (
                    <Contador
                      quantidade={contarPendencias(pendencias, tela.pendencia)}
                      tela={tela.pendencia}
                    />
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
      {!recolhida && <ResumoDaBase />}
    </nav>
  )
}
