import { Link } from 'react-router'

import { Logo } from '../../components/Logo'
import estilos from './RodapePublico.module.css'

const LINKS = [
  { caminho: '/como-funciona', rotulo: 'Como funciona' },
  { caminho: '/a-cidade-em-numeros', rotulo: 'A cidade em números' },
  { caminho: '/contribuir', rotulo: 'Relatar um problema' },
  { caminho: '/cadastrar', rotulo: 'Criar conta' },
  { caminho: '/entrar', rotulo: 'Entrar' },
  { caminho: '/entrar/gestao', rotulo: 'Acesso da gestão' },
] as const

export function RodapePublico() {
  return (
    <footer className={estilos.rodape}>
      <div className={`conteudo ${estilos.grade}`}>
        <div className={estilos.marca}>
          <Logo variante="branco" altura={28} />
          <p>
            Relatos e números das demandas urbanas do Recife, para quem mora na cidade e para quem
            decide na gestão pública.
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
