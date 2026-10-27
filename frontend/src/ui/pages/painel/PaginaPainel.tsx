import { Link, NavLink } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { rotuloDoPerfil, type Usuario } from '../../../domain/usuario'
import { Logo } from '../../components/Logo'
import { ROTA_INICIAL_DO_PAINEL } from '../../components/navegacao'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { TELAS_DO_PAINEL } from '../../conteudo/telasDoPainel'
import { MenuDoUsuario } from './MenuDoUsuario'
import estilos from './PaginaPainel.module.css'

interface Propriedades {
  usuario: Usuario
  aoSair: () => void
}

function CabecalhoDoPainel({ usuario, aoSair }: Propriedades) {
  return (
    <header className={estilos.cabecalho}>
      <div className={estilos.barra}>
        <Link to={ROTA_INICIAL_DO_PAINEL} className={estilos.marca} aria-label="Visão geral">
          <Logo variante="branco" altura={28} />
        </Link>
        <nav aria-label="Telas do painel" className={estilos.navegacao}>
          <NavLink to={ROTA_INICIAL_DO_PAINEL} end>
            Visão geral
          </NavLink>
        </nav>
        <MenuDoUsuario usuario={usuario} aoSair={aoSair} />
      </div>
    </header>
  )
}

export function PaginaPainel() {
  useTituloDaPagina('Visão geral')
  const { estado, sair } = useSessao()
  if (estado.situacao !== 'autenticada') return null
  const { usuario } = estado

  return (
    <>
      <PularParaConteudo />
      <CabecalhoDoPainel usuario={usuario} aoSair={sair} />
      <main id={ID_DO_CONTEUDO_PRINCIPAL} className={estilos.principal} tabIndex={-1}>
        <div className={estilos.conteudo}>
          <h1 className={estilos.titulo}>Visão geral</h1>
          <p className={estilos.pergunta}>
            Onde as demandas do Recife se repetem, demoram ou ficam sem resposta.
          </p>
          <div className={estilos.grade}>
            <section className={estilos.bloco} aria-labelledby="titulo-construcao">
              <h2 id="titulo-construcao">Os indicadores estão em construção</h2>
              <p>
                O acesso ao painel já funciona. As telas com os dados do Recife entram nas próximas
                versões:
              </p>
              <ul className={estilos.telas}>
                {TELAS_DO_PAINEL.map(({ nome, mostra }) => (
                  <li key={nome}>
                    <h3>{nome}</h3>
                    <p>{mostra}</p>
                  </li>
                ))}
              </ul>
            </section>
            <aside className={`${estilos.bloco} ${estilos.sessao}`} aria-labelledby="titulo-sessao">
              <h2 id="titulo-sessao">Sua sessão</h2>
              <p>
                Você entrou como {usuario.nome} ({rotuloDoPerfil(usuario.perfil)}). Para encerrar o
                acesso neste navegador, abra o menu com o seu nome e escolha Sair.
              </p>
            </aside>
          </div>
        </div>
      </main>
    </>
  )
}
