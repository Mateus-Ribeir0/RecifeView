import { NavLink } from 'react-router'

import { useCatalogo } from '../../../application/consultas/usePainel'
import { formatarNumero } from '../../../domain/formatacao'
import { Icone } from '../../components/Icone'
import { GRUPOS_DE_TELAS, ROTA_RAIZ_DO_PAINEL } from '../../conteudo/telasDoPainel'
import estilos from './BarraLateral.module.css'

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
