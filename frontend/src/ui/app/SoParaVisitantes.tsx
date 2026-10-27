import { Navigate, Outlet, useLocation } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import { lerEstadoDeNavegacao, ROTA_INICIAL_DO_PAINEL } from '../components/navegacao'
import { VerificandoSessao } from '../components/VerificandoSessao'

export function SoParaVisitantes() {
  const { estado } = useSessao()
  const { destino } = lerEstadoDeNavegacao(useLocation().state)

  if (estado.situacao === 'verificando') return <VerificandoSessao />
  if (estado.situacao === 'autenticada') {
    return <Navigate to={destino ?? ROTA_INICIAL_DO_PAINEL} replace />
  }
  return <Outlet />
}
