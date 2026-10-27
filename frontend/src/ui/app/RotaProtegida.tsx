import { Navigate, Outlet, useLocation } from 'react-router'

import { useSessao } from '../../application/autenticacao/useSessao'
import type { EstadoDeNavegacao } from '../components/navegacao'
import { VerificandoSessao } from '../components/VerificandoSessao'

const ROTA_DE_TROCA_DE_SENHA = '/definir-senha'

export function RotaProtegida() {
  const { estado } = useSessao()
  const { pathname } = useLocation()

  if (estado.situacao === 'verificando') return <VerificandoSessao />
  if (estado.situacao === 'anonima') {
    const destino: EstadoDeNavegacao = { destino: pathname, motivo: estado.motivo }
    return <Navigate to="/entrar" replace state={destino} />
  }
  if (estado.usuario.deveTrocarSenha && pathname !== ROTA_DE_TROCA_DE_SENHA) {
    const destino: EstadoDeNavegacao = { destino: pathname }
    return <Navigate to={ROTA_DE_TROCA_DE_SENHA} replace state={destino} />
  }
  return <Outlet />
}
