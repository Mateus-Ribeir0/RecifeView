import { Link } from 'react-router'

import { Logo } from '../../components/Logo'
import estilos from './RodapePublico.module.css'

const LINKS = [
  { caminho: '/o-que-muda', rotulo: 'O que muda' },
  { caminho: '/plataforma', rotulo: 'A plataforma' },
  { caminho: '/dados-e-confianca', rotulo: 'Dados e confiança' },
  { caminho: '/contribuir', rotulo: 'Relatar um problema' },
  { caminho: '/entrar', rotulo: 'Entrar no painel' },
] as const

export function RodapePublico() {
  return (
    <footer className={estilos.rodape}>
      <div className={`conteudo ${estilos.grade}`}>
        <div className={estilos.marca}>
          <Logo variante="branco" altura={28} />
          <p>
            Plataforma de análise das demandas urbanas do Recife, feita para quem decide na gestão
            pública.
          </p>
        </div>
        <nav aria-label="Páginas do site, no rodapé">
          <h2 className={estilos.titulo}>Navegue</h2>
          <ul className={estilos.links}>
            {LINKS.map(({ caminho, rotulo }) => (
              <li key={caminho}>
                <Link to={caminho}>{rotulo}</Link>
              </li>
            ))}
          </ul>
        </nav>
        <div>
          <h2 className={estilos.titulo}>Dados</h2>
          <p>
            Portal de Dados Abertos do Recife (licença ODbL), Câmara Municipal do Recife (SAGL) e
            IBGE (Censo 2022).
          </p>
        </div>
      </div>
      <div className={`conteudo ${estilos.base}`}>
        <p>RecifeView</p>
        <p>O painel organiza as evidências. A decisão continua com a gestão.</p>
      </div>
    </footer>
  )
}
