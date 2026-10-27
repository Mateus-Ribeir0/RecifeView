import { Link } from 'react-router'

import { LinkDeBotao } from '../../components/LinkDeBotao'
import { Logo } from '../../components/Logo'
import estilos from './CabecalhoPublico.module.css'

const SECOES = [
  { ancora: '#problema', rotulo: 'O problema' },
  { ancora: '#dados', rotulo: 'O que os dados mostram' },
  { ancora: '#painel', rotulo: 'O painel' },
  { ancora: '#fontes', rotulo: 'Fontes' },
  { ancora: '#projeto', rotulo: 'O projeto' },
] as const

export function CabecalhoPublico() {
  return (
    <header className={estilos.cabecalho}>
      <div className={`conteudo ${estilos.barra}`}>
        <Link to="/" className={estilos.marca} aria-label="RecifeView, página inicial">
          <Logo altura={32} />
        </Link>
        <nav aria-label="Seções da página" className={estilos.navegacao}>
          <ul>
            {SECOES.map((secao) => (
              <li key={secao.ancora}>
                <a href={secao.ancora}>{secao.rotulo}</a>
              </li>
            ))}
          </ul>
        </nav>
        <LinkDeBotao para="/entrar" variante="secundario" compacto>
          Entrar
        </LinkDeBotao>
      </div>
    </header>
  )
}
