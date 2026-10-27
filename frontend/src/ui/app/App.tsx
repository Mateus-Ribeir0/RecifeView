import { createBrowserRouter, Outlet, ScrollRestoration } from 'react-router'
import { RouterProvider } from 'react-router/dom'

import { ProvedorDeSessao } from '../../application/autenticacao/ProvedorDeSessao'
import { criarServicoDeAutenticacao } from '../../infrastructure/api/autenticacao'
import { ClienteHttp } from '../../infrastructure/api/cliente'
import { PaginaAjudaDeAcesso } from '../pages/ajuda-de-acesso/PaginaAjudaDeAcesso'
import { PaginaDefinirSenha } from '../pages/definir-senha/PaginaDefinirSenha'
import { PaginaEntrar } from '../pages/entrar/PaginaEntrar'
import { PaginaInicial } from '../pages/inicio/PaginaInicial'
import { PaginaNaoEncontrada } from '../pages/nao-encontrada/PaginaNaoEncontrada'
import { PaginaPainel } from '../pages/painel/PaginaPainel'
import { RotaProtegida } from './RotaProtegida'
import { SoParaVisitantes } from './SoParaVisitantes'

const URL_DA_API = import.meta.env.VITE_URL_DA_API ?? '/api/v1'

const servicoDeAutenticacao = criarServicoDeAutenticacao(new ClienteHttp(URL_DA_API))

function Raiz() {
  return (
    <>
      <ScrollRestoration />
      <Outlet />
    </>
  )
}

const roteador = createBrowserRouter([
  {
    element: <Raiz />,
    children: [
      { index: true, element: <PaginaInicial /> },
      { element: <SoParaVisitantes />, children: [{ path: 'entrar', element: <PaginaEntrar /> }] },
      { path: 'entrar/ajuda', element: <PaginaAjudaDeAcesso /> },
      {
        element: <RotaProtegida />,
        children: [
          { path: 'definir-senha', element: <PaginaDefinirSenha /> },
          { path: 'painel', element: <PaginaPainel /> },
        ],
      },
      { path: '*', element: <PaginaNaoEncontrada /> },
    ],
  },
])

export function App() {
  return (
    <ProvedorDeSessao servico={servicoDeAutenticacao}>
      <RouterProvider router={roteador} />
    </ProvedorDeSessao>
  )
}
