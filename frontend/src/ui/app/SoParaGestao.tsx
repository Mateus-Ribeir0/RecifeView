import { Navigate, Outlet } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import { eDaGestao, inicioDoPerfil } from '../../domain/usuario'

export function SoParaGestao() {
  const { estado } = useSessao()
  if (estado.situacao === 'autenticada' && !eDaGestao(estado.usuario.perfil)) {
    return <Navigate to={inicioDoPerfil(estado.usuario.perfil)} replace />
  }
  return <Outlet />
}
