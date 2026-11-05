import { NavLink, useLocation } from 'react-router'

import { GRUPOS_DE_TELAS } from '../../conteudo/telasDoPainel'
import estilos from './BarraLateral.module.css'
import { FiltrosGlobais } from './FiltrosGlobais'

const ROTA_DE_IMPORTACOES = '/painel/importacoes'
const ROTA_DA_NOVA_IMPORTACAO = `${ROTA_DE_IMPORTACOES}/nova`

interface Propriedades {
  aoNavegar: () => void
}

function classeDaParte({ isActive }: { isActive: boolean }) {
  return isActive ? `${estilos.parte} ${estilos.parteAtiva}` : estilos.parte
}

function NavegacaoDoPainel({ aoNavegar }: Propriedades) {
  return (
    <>
      <nav aria-label="Telas do painel" className={estilos.navegacao}>
        {GRUPOS_DE_TELAS.map(({ grupo, telas }) => (
          <div key={grupo}>
            <p className={estilos.grupo}>{grupo}</p>
            <ul>
              {telas.map((tela) => (
                <li key={tela.caminho}>
                  <NavLink
                    to={tela.caminho}
                    end
                    className={estilos.item}
                    title={tela.mostra}
                    onClick={aoNavegar}
                  >
                    {tela.nome}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      <FiltrosGlobais />
    </>
  )
}

function NavegacaoDasImportacoes({ aoNavegar }: Propriedades) {
  return (
    <nav aria-label="Importações" className={estilos.navegacao}>
      <div>
        <p className={estilos.grupo}>Trazer dados novos</p>
        <ul>
          <li>
            <NavLink to={ROTA_DA_NOVA_IMPORTACAO} className={estilos.item} onClick={aoNavegar}>
              Nova importação
            </NavLink>
          </li>
          <li>
            <NavLink to={ROTA_DE_IMPORTACOES} end className={estilos.item} onClick={aoNavegar}>
              Histórico
            </NavLink>
          </li>
        </ul>
      </div>
      <p className={estilos.explicacao}>
        Arquivos das fontes do Recife entram na mesma base do painel. O que não bater vira pergunta
        antes da carga.
      </p>
    </nav>
  )
}

export function BarraLateral({ aoNavegar }: Propriedades) {
  const { pathname } = useLocation()
  const emImportacoes = pathname.startsWith(ROTA_DE_IMPORTACOES)

  return (
    <div className={estilos.lateral}>
      <nav aria-label="Áreas" className={estilos.partes}>
        <NavLink
          to="/painel"
          className={() => classeDaParte({ isActive: !emImportacoes })}
          aria-current={emImportacoes ? undefined : 'true'}
          onClick={aoNavegar}
        >
          Painel
        </NavLink>
        <NavLink
          to={ROTA_DE_IMPORTACOES}
          className={() => classeDaParte({ isActive: emImportacoes })}
          aria-current={emImportacoes ? 'true' : undefined}
          onClick={aoNavegar}
        >
          Importações
        </NavLink>
      </nav>
      {emImportacoes ? (
        <NavegacaoDasImportacoes aoNavegar={aoNavegar} />
      ) : (
        <NavegacaoDoPainel aoNavegar={aoNavegar} />
      )}
    </div>
  )
}
