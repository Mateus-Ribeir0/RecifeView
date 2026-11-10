import { Suspense, type ReactNode } from 'react'
import { Link } from 'react-router'

import fotoDoRecife from '../assets/imagens/recife-skyline.jpg'
import { MapaDosBairros } from '../map/MapaDosBairros'
import estilos from './LayoutDeAcesso.module.css'
import { Logo } from './Logo'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from './PularParaConteudo'

export type TomDoAcesso = 'cidade' | 'gestao'

const APRESENTACAO: Readonly<
  Record<TomDoAcesso, { selo: string; frase: string; detalhe: string }>
> = {
  cidade: {
    selo: 'Área do cidadão',
    frase: 'Acompanhe o que foi relatado no seu bairro.',
    detalhe:
      'Veja os problemas de rua que outras pessoas relataram, em que pé está cada um e como o seu bairro se compara com o Recife.',
  },
  gestao: {
    selo: 'Área da gestão',
    frase: 'Onde as demandas do Recife se repetem, demoram ou ficam sem resposta.',
    detalhe:
      'Painel, pente fino dos relatos e importação de arquivos, só para contas criadas pela administração.',
  },
}

interface Propriedades {
  tom?: TomDoAcesso
  children: ReactNode
}

export function LayoutDeAcesso({ tom = 'cidade', children }: Propriedades) {
  const { selo, frase, detalhe } = APRESENTACAO[tom]

  return (
    <div className={estilos.layout} data-tom={tom}>
      <PularParaConteudo />
      <aside className={estilos.painel} aria-label="Sobre o RecifeView">
        {tom === 'cidade' && <img src={fotoDoRecife} alt="" className={estilos.foto} />}
        <Link
          to="/"
          className={estilos.marca}
          aria-label="RecifeView, voltar para a página inicial"
        >
          <Logo variante="branco" altura={32} />
        </Link>
        <div className={estilos.apresentacao}>
          <p className={estilos.selo}>{selo}</p>
          <p className={estilos.frase}>{frase}</p>
          <p className={estilos.detalhe}>{detalhe}</p>
        </div>
        {tom === 'gestao' && (
          <div className={estilos.mapa} aria-hidden="true">
            <Suspense fallback={null}>
              <MapaDosBairros tom="sobreAzul" descricao="Bairros do Recife" />
            </Suspense>
          </div>
        )}
      </aside>
      <main id={ID_DO_CONTEUDO_PRINCIPAL} className={estilos.principal} tabIndex={-1}>
        <div className={estilos.coluna}>{children}</div>
      </main>
    </div>
  )
}
