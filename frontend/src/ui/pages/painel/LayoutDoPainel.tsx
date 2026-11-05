import { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { Icone } from '../../components/Icone'
import { Logo } from '../../components/Logo'
import { ROTA_INICIAL_DO_PAINEL } from '../../components/navegacao'
import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { filtrosDaRota } from '../../conteudo/telasDoPainel'
import { BarraDeFiltros } from './BarraDeFiltros'
import { BarraLateral } from './BarraLateral'
import estilos from './LayoutDoPainel.module.css'
import { MenuDoUsuario } from './MenuDoUsuario'
import { RodapeDoPainel } from './RodapeDoPainel'
import { useLateralRecolhida } from './useLateralRecolhida'

const CONSULTA_DA_GAVETA = '(max-width: 1039px)'

export function LayoutDoPainel() {
  const { estado, sair } = useSessao()
  const { pathname } = useLocation()
  const [recolhida, alternarRecolhida] = useLateralRecolhida()
  const [gavetaAberta, definirGavetaAberta] = useState(false)
  if (estado.situacao !== 'autenticada') return null

  function alternarMenu() {
    if (window.matchMedia(CONSULTA_DA_GAVETA).matches) definirGavetaAberta((atual) => !atual)
    else alternarRecolhida()
  }

  const filtros = filtrosDaRota(pathname)
  const classesDaLateral = [
    estilos.lateral,
    recolhida ? estilos.lateralRecolhida : '',
    gavetaAberta ? estilos.gavetaAberta : '',
  ].join(' ')

  return (
    <>
      <PularParaConteudo />
      <header className={estilos.cabecalho}>
        <button
          type="button"
          className={estilos.menu}
          aria-label={gavetaAberta || !recolhida ? 'Recolher o menu' : 'Abrir o menu'}
          aria-expanded={gavetaAberta || !recolhida}
          onClick={alternarMenu}
        >
          <Icone nome={gavetaAberta ? 'fechar' : 'menu'} tamanho={24} />
        </button>
        <Link to={ROTA_INICIAL_DO_PAINEL} className={estilos.marca} aria-label="Início do painel">
          <Logo variante="branco" altura={26} />
        </Link>
        <MenuDoUsuario usuario={estado.usuario} aoSair={sair} />
      </header>
      <div className={estilos.corpo}>
        {gavetaAberta && (
          <button
            type="button"
            className={estilos.fundoDaGaveta}
            aria-label="Fechar o menu"
            onClick={() => definirGavetaAberta(false)}
          />
        )}
        <aside className={classesDaLateral}>
          <BarraLateral
            recolhida={recolhida && !gavetaAberta}
            aoNavegar={() => definirGavetaAberta(false)}
          />
        </aside>
        <main id={ID_DO_CONTEUDO_PRINCIPAL} className={estilos.principal} tabIndex={-1}>
          {filtros.length > 0 && <BarraDeFiltros campos={filtros} />}
          <div className={estilos.conteudo}>
            <Outlet />
            <RodapeDoPainel />
          </div>
        </main>
      </div>
    </>
  )
}
