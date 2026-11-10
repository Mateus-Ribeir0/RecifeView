import { Link, NavLink, Outlet } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { eDaGestao } from '../../../domain/usuario'
import { Logo } from '../../components/Logo'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { MenuDoUsuario } from '../painel/MenuDoUsuario'
import estilos from './LayoutDaCidade.module.css'

const ABAS = [
  { caminho: '/cidade', rotulo: 'Relatos da cidade' },
  { caminho: '/cidade/meu-bairro', rotulo: 'Meu bairro' },
  { caminho: '/cidade/relatar', rotulo: 'Relatar um problema' },
] as const

export function LayoutDaCidade() {
  const { estado, sair } = useSessao()
  if (estado.situacao !== 'autenticada') return null
  const { usuario } = estado

  return (
    <>
      <PularParaConteudo />
      <header className={estilos.cabecalho}>
        <div className={`conteudo ${estilos.barra}`}>
          <Link to="/cidade" className={estilos.marca} aria-label="Início da área do cidadão">
            <Logo variante="branco" altura={28} />
          </Link>
          <span className={estilos.selo}>Área do cidadão</span>
          <nav aria-label="Seções da área do cidadão" className={estilos.navegacao}>
            <ul>
              {ABAS.map(({ caminho, rotulo }) => (
                <li key={caminho}>
                  <NavLink to={caminho} end={caminho === '/cidade'}>
                    {rotulo}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
          {eDaGestao(usuario.perfil) && (
            <Link to="/painel" className={estilos.atalhoDaGestao}>
              Painel da gestão
            </Link>
          )}
          <MenuDoUsuario usuario={usuario} aoSair={() => void sair()} />
        </div>
      </header>
      <main id={ID_DO_CONTEUDO_PRINCIPAL} tabIndex={-1} className={estilos.principal}>
        <div className="conteudo">
          <Outlet />
        </div>
      </main>
      <footer className={estilos.rodape}>
        <div className="conteudo">
          <p>
            Relatos do formulário do RecifeView e dados abertos da Prefeitura do Recife (ODbL),
            Câmara Municipal e IBGE. Quem relatou nunca é identificado.
          </p>
        </div>
      </footer>
    </>
  )
}
