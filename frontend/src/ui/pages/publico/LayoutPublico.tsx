import { Outlet, useLocation } from 'react-router'

import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { CabecalhoPublico } from './CabecalhoPublico'
import estilos from './LayoutPublico.module.css'
import { RodapePublico } from './RodapePublico'

export function LayoutPublico() {
  const { pathname } = useLocation()

  return (
    <>
      <PularParaConteudo />
      <CabecalhoPublico />
      <main id={ID_DO_CONTEUDO_PRINCIPAL} tabIndex={-1} key={pathname} className={estilos.pagina}>
        <Outlet />
      </main>
      <RodapePublico />
    </>
  )
}
