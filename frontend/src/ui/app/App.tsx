import { createBrowserRouter, Outlet, ScrollRestoration } from 'react-router'
import { RouterProvider } from 'react-router/dom'

import { ProvedorDeSessao } from '../../application/autenticacao/ProvedorDeSessao'
import { ContextoDasContribuicoes } from '../../application/contribuicoes/contexto'
import { PaginaAjudaDeAcesso } from '../pages/ajuda-de-acesso/PaginaAjudaDeAcesso'
import { PaginaDefinirSenha } from '../pages/definir-senha/PaginaDefinirSenha'
import { PaginaEntrar } from '../pages/entrar/PaginaEntrar'
import { PaginaInicial } from '../pages/inicio/PaginaInicial'
import { PaginaNaoEncontrada } from '../pages/nao-encontrada/PaginaNaoEncontrada'
import { RotaProtegida } from './RotaProtegida'
import { servicoDeAutenticacao, servicoDeContribuicoes } from './servicos'
import { SoParaVisitantes } from './SoParaVisitantes'

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
          {
            path: 'painel',
            lazy: async () => ({
              Component: (await import('./MontagemDoPainel')).MontagemDoPainel,
            }),
            children: [
              {
                index: true,
                lazy: async () => ({
                  Component: (await import('../pages/painel/inicio/PaginaInicioDoPainel'))
                    .PaginaInicioDoPainel,
                }),
              },
              {
                path: 'war-room',
                lazy: async () => ({
                  Component: (await import('../pages/painel/war-room/PaginaWarRoom')).PaginaWarRoom,
                }),
              },
              {
                path: 'retorno',
                lazy: async () => ({
                  Component: (await import('../pages/painel/retorno/PaginaRetorno')).PaginaRetorno,
                }),
              },
              {
                path: 'reincidencia',
                lazy: async () => ({
                  Component: (await import('../pages/painel/reincidencia/PaginaReincidencia'))
                    .PaginaReincidencia,
                }),
              },
              {
                path: 'prazos',
                lazy: async () => ({
                  Component: (await import('../pages/painel/prazos/PaginaPrazos')).PaginaPrazos,
                }),
              },
              {
                path: 'territorio',
                lazy: async () => ({
                  Component: (await import('../pages/painel/territorio/PaginaTerritorio'))
                    .PaginaTerritorio,
                }),
              },
              {
                path: 'prioridade',
                lazy: async () => ({
                  Component: (await import('../pages/painel/prioridade/PaginaPrioridade'))
                    .PaginaPrioridade,
                }),
              },
              {
                path: 'sobre-os-dados',
                lazy: async () => ({
                  Component: (await import('../pages/painel/sobre/PaginaSobreOsDados'))
                    .PaginaSobreOsDados,
                }),
              },
              {
                path: 'contribuicoes',
                lazy: async () => ({
                  Component: (await import('../pages/contribuicoes/PaginaContribuicoes'))
                    .PaginaContribuicoes,
                }),
              },
              {
                path: 'importacoes',
                lazy: async () => ({
                  Component: (await import('../pages/importacoes/PaginaHistorico')).PaginaHistorico,
                }),
              },
              {
                path: 'importacoes/nova',
                lazy: async () => ({
                  Component: (await import('../pages/importacoes/PaginaNovaImportacao'))
                    .PaginaNovaImportacao,
                }),
              },
              {
                path: 'importacoes/:id',
                lazy: async () => ({
                  Component: (await import('../pages/importacoes/PaginaImportacao'))
                    .PaginaImportacao,
                }),
              },
            ],
          },
        ],
      },
      { path: '*', element: <PaginaNaoEncontrada /> },
    ],
  },
])

export function App() {
  return (
    <ProvedorDeSessao servico={servicoDeAutenticacao}>
      <ContextoDasContribuicoes value={servicoDeContribuicoes}>
        <RouterProvider router={roteador} />
      </ContextoDasContribuicoes>
    </ProvedorDeSessao>
  )
}
