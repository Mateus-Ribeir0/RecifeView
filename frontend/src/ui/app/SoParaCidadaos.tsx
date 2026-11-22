import { Navigate, Outlet } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import { inicioDoPerfil } from '../../domain/usuario'

export function SoParaCidadaos() {
  const { estado } = useSessao()
  if (estado.situacao === 'autenticada' && estado.usuario.perfil !== 'CIDADAO') {
    return <Navigate to={inicioDoPerfil(estado.usuario.perfil)} replace />
  }
  return <Outlet />
}
