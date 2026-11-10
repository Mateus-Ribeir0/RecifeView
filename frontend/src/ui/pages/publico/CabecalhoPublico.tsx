import { useState } from 'react'
import { Link, NavLink } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { inicioDoPerfil } from '../../../domain/usuario'
import { Icone } from '../../components/Icone'
import { LinkDeBotao } from '../../components/LinkDeBotao'
import { Logo } from '../../components/Logo'
import estilos from './CabecalhoPublico.module.css'

const ABAS = [
  { caminho: '/', rotulo: 'Início' },
  { caminho: '/como-funciona', rotulo: 'Como funciona' },
  { caminho: '/a-cidade-em-numeros', rotulo: 'A cidade em números' },
  { caminho: '/contribuir', rotulo: 'Relatar um problema' },
] as const

interface Acao {
  caminho: string
  rotulo: string
}

function useAcoes(): readonly Acao[] {
  const { estado } = useSessao()
  if (estado.situacao === 'autenticada') {
    return [{ caminho: inicioDoPerfil(estado.usuario.perfil), rotulo: 'Minha área' }]
  }
  return [
    { caminho: '/entrar', rotulo: 'Entrar' },
    { caminho: '/cadastrar', rotulo: 'Criar conta' },
  ]
}

export function CabecalhoPublico() {
  const [aberto, definirAberto] = useState(false)
  const acoes = useAcoes()
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
            {acoes.map(({ caminho, rotulo }) => (
              <li key={caminho} className={estilos.soNoMenu}>
                <NavLink to={caminho} onClick={fechar}>
                  {rotulo}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className={estilos.acoes}>
          {acoes.map(({ caminho, rotulo }, indice) => (
            <LinkDeBotao
              key={caminho}
              para={caminho}
              variante={indice === acoes.length - 1 ? 'primario' : 'secundario'}
              compacto
            >
              {rotulo}
            </LinkDeBotao>
          ))}
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
