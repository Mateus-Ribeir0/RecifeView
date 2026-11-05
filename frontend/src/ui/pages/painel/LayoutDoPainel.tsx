import { useState } from 'react'
import { Link, Outlet } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { Logo } from '../../components/Logo'
import { ROTA_INICIAL_DO_PAINEL } from '../../components/navegacao'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { BarraLateral } from './BarraLateral'
import estilos from './LayoutDoPainel.module.css'
import { MenuDoUsuario } from './MenuDoUsuario'
import { RodapeDoPainel } from './RodapeDoPainel'

export function LayoutDoPainel() {
  const { estado, sair } = useSessao()
  const [lateralFechada, definirLateralFechada] = useState(false)
  const [gavetaAberta, definirGavetaAberta] = useState(false)
  if (estado.situacao !== 'autenticada') return null

  const classesDaLateral = [
    estilos.lateral,
    lateralFechada ? estilos.lateralFechada : '',
    gavetaAberta ? estilos.gavetaAberta : '',
  ].join(' ')

  return (
    <>
      <PularParaConteudo />
      <header className={estilos.cabecalho}>
        <button
          type="button"
          className={estilos.abrirLateral}
          aria-expanded={gavetaAberta}
          onClick={() => definirGavetaAberta((atual) => !atual)}
        >
          Menu e filtros
        </button>
        <button
          type="button"
          className={estilos.recolher}
          aria-pressed={lateralFechada}
          onClick={() => definirLateralFechada((atual) => !atual)}
        >
          {lateralFechada ? 'Mostrar barra lateral' : 'Recolher barra lateral'}
        </button>
        <Link to={ROTA_INICIAL_DO_PAINEL} className={estilos.marca} aria-label="Início do painel">
          <Logo variante="branco" altura={28} />
        </Link>
        <MenuDoUsuario usuario={estado.usuario} aoSair={sair} />
      </header>
      <div className={estilos.corpo}>
        <aside className={classesDaLateral} aria-label="Navegação e filtros">
          <BarraLateral aoNavegar={() => definirGavetaAberta(false)} />
        </aside>
        <main id={ID_DO_CONTEUDO_PRINCIPAL} className={estilos.principal} tabIndex={-1}>
          <div className={estilos.conteudo}>
            <Outlet />
            <RodapeDoPainel />
          </div>
        </main>
      </div>
    </>
  )
}
