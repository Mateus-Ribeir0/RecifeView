import { Navigate, Outlet, useLocation } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import { inicioDoPerfil, podeAbrir } from '../../domain/usuario'
import { lerEstadoDeNavegacao } from '../components/navegacao'
import { VerificandoSessao } from '../components/VerificandoSessao'

export function SoParaVisitantes() {
  const { estado } = useSessao()
  const { destino } = lerEstadoDeNavegacao(useLocation().state)

  if (estado.situacao === 'verificando') return <VerificandoSessao />
  if (estado.situacao === 'autenticada') {
    const { perfil } = estado.usuario
    const alvo = destino && podeAbrir(perfil, destino) ? destino : inicioDoPerfil(perfil)
    return <Navigate to={alvo} replace />
  }
  return <Outlet />
}
