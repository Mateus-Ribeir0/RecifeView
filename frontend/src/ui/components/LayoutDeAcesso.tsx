import { Suspense, type ReactNode } from 'react'
import { Link } from 'react-router'

import { MapaDosBairros } from '../map/MapaDosBairros'
import estilos from './LayoutDeAcesso.module.css'
import { Logo } from './Logo'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from './PularParaConteudo'

interface Propriedades {
  children: ReactNode
}

export function LayoutDeAcesso({ children }: Propriedades) {
  return (
    <div className={estilos.layout}>
      <PularParaConteudo />
      <aside className={estilos.painel} aria-label="Sobre o RecifeView">
        <Link
          to="/"
          className={estilos.marca}
          aria-label="RecifeView, voltar para a página inicial"
        >
          <Logo variante="branco" altura={32} />
        </Link>
        <div className={estilos.apresentacao}>
          <p className={estilos.frase}>
            Onde as demandas do Recife se repetem, demoram ou ficam sem resposta.
          </p>
          <p className={estilos.detalhe}>
            Mapa por bairro, prazos, recorrências e o caminho das indicações da Câmara até a
            Prefeitura.
          </p>
        </div>
        <div className={estilos.mapa} aria-hidden="true">
          <Suspense fallback={null}>
            <MapaDosBairros tom="sobreAzul" descricao="Bairros do Recife" />
          </Suspense>
        </div>
      </aside>
      <main id={ID_DO_CONTEUDO_PRINCIPAL} className={estilos.principal} tabIndex={-1}>
        <div className={estilos.coluna}>{children}</div>
      </main>
    </div>
  )
}
