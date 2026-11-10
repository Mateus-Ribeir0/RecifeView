import { Navigate, Outlet } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import { eDaGestao, ROTA_INICIAL_DA_GESTAO } from '../../domain/usuario'

export function SoParaCidadaos() {
  const { estado } = useSessao()
  if (estado.situacao === 'autenticada' && eDaGestao(estado.usuario.perfil)) {
    return <Navigate to={ROTA_INICIAL_DA_GESTAO} replace />
  }
  return <Outlet />
}
