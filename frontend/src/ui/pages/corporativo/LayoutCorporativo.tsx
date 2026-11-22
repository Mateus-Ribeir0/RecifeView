import { Link, NavLink, Outlet } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { ROTA_INICIAL_CORPORATIVA } from '../../../domain/usuario'
import { Logo } from '../../components/Logo'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { Sino } from '../../components/Sino'
import { MenuDoUsuario } from '../painel/MenuDoUsuario'
import estilos from './LayoutCorporativo.module.css'

const ABAS = [
  { caminho: ROTA_INICIAL_CORPORATIVA, rotulo: 'Visão geral' },
  { caminho: `${ROTA_INICIAL_CORPORATIVA}/ocorrencias`, rotulo: 'Ocorrências' },
  { caminho: `${ROTA_INICIAL_CORPORATIVA}/resolvidas`, rotulo: 'Resolvidas' },
  { caminho: `${ROTA_INICIAL_CORPORATIVA}/dados`, rotulo: 'Dados do órgão' },
] as const

export function LayoutCorporativo() {
  const { estado, sair } = useSessao()
  if (estado.situacao !== 'autenticada') return null
  const { usuario } = estado

  return (
    <>
      <PularParaConteudo />
      <header className={estilos.cabecalho}>
        <div className={`conteudo ${estilos.barra}`}>
          <Link
            to={ROTA_INICIAL_CORPORATIVA}
            className={estilos.marca}
            aria-label="Início da área corporativa"
          >
            <Logo variante="branco" altura={28} />
          </Link>
          <span className={estilos.selo}>Área corporativa</span>
          {usuario.nomeDoOrgao && <span className={estilos.orgao}>{usuario.nomeDoOrgao}</span>}
          <nav aria-label="Seções da área corporativa" className={estilos.navegacao}>
            <ul>
              {ABAS.map(({ caminho, rotulo }) => (
                <li key={caminho}>
                  <NavLink to={caminho} end={caminho === ROTA_INICIAL_CORPORATIVA}>
                    {rotulo}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
          <div className={estilos.ferramentas}>
            <Sino />
            <MenuDoUsuario usuario={usuario} aoSair={() => void sair()} />
          </div>
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
            Ocorrências encaminhadas pela gestão da Prefeitura do Recife pelo RecifeView. Quem fez o
            pedido nunca é identificado: a área mostra o bairro, a rua oficial com a faixa de
            numeração e quantas pessoas acompanham.
          </p>
        </div>
      </footer>
    </>
  )
}
