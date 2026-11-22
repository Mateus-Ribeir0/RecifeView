import { Navigate, Outlet } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import { eCorporativo, inicioDoPerfil } from '../../domain/usuario'

export function SoParaCorporativos() {
  const { estado } = useSessao()
  if (estado.situacao === 'autenticada' && !eCorporativo(estado.usuario.perfil)) {
    return <Navigate to={inicioDoPerfil(estado.usuario.perfil)} replace />
  }
  return <Outlet />
}
