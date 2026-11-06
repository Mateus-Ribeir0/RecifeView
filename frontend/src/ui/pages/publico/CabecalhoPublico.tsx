import { useState } from 'react'
import { Link, NavLink } from 'react-router'

import { Icone } from '../../components/Icone'
import { LinkDeBotao } from '../../components/LinkDeBotao'
import { Logo } from '../../components/Logo'
import estilos from './CabecalhoPublico.module.css'

const ABAS = [
  { caminho: '/', rotulo: 'Início' },
  { caminho: '/o-que-muda', rotulo: 'O que muda' },
  { caminho: '/plataforma', rotulo: 'A plataforma' },
  { caminho: '/dados-e-confianca', rotulo: 'Dados e confiança' },
] as const

const ACOES_NO_MENU = [
  { caminho: '/contribuir', rotulo: 'Relatar um problema' },
  { caminho: '/entrar', rotulo: 'Entrar' },
] as const

export function CabecalhoPublico() {
  const [aberto, definirAberto] = useState(false)
  const fechar = () => definirAberto(false)

  return (
    <header className={estilos.cabecalho}>
      <div className={`conteudo ${estilos.barra}`}>
        <Link to="/" className={estilos.marca} aria-label="RecifeView, página inicial">
          <Logo altura={32} />
        </Link>
        <nav
          aria-label="Páginas do site"
          className={estilos.navegacao}
          data-aberta={aberto || undefined}
        >
          <ul>
            {ABAS.map(({ caminho, rotulo }) => (
              <li key={caminho}>
                <NavLink to={caminho} end={caminho === '/'} onClick={fechar}>
                  {rotulo}
                </NavLink>
              </li>
            ))}
            {ACOES_NO_MENU.map(({ caminho, rotulo }) => (
              <li key={caminho} className={estilos.soNoMenu}>
                <NavLink to={caminho} onClick={fechar}>
                  {rotulo}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className={estilos.acoes}>
          <LinkDeBotao para="/contribuir" compacto>
            Relatar um problema
          </LinkDeBotao>
          <LinkDeBotao para="/entrar" variante="secundario" compacto>
            Entrar
          </LinkDeBotao>
        </div>
        <button
          type="button"
          className={estilos.botaoDoMenu}
          aria-expanded={aberto}
          aria-label={aberto ? 'Fechar o menu' : 'Abrir o menu'}
          onClick={() => definirAberto((atual) => !atual)}
        >
          <Icone nome={aberto ? 'fechar' : 'menu'} tamanho={24} />
        </button>
      </div>
    </header>
  )
}
