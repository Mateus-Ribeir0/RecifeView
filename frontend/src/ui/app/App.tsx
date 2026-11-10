import { createBrowserRouter, Navigate, Outlet, ScrollRestoration } from 'react-router'
import { RouterProvider } from 'react-router/dom'

import { ProvedorDeSessao } from '../../application/autenticacao/ProvedorDeSessao'
import { ContextoDaCidade } from '../../application/cidade/contexto'
import { ContextoDasContribuicoes } from '../../application/contribuicoes/contexto'
import { PaginaAjudaDeAcesso } from '../pages/ajuda-de-acesso/PaginaAjudaDeAcesso'
import { PaginaCadastrar } from '../pages/cadastrar/PaginaCadastrar'
import { LayoutDaCidade } from '../pages/cidade/LayoutDaCidade'
import { PaginaConfirmarEmail } from '../pages/confirmar-email/PaginaConfirmarEmail'
import { PaginaDefinirSenha } from '../pages/definir-senha/PaginaDefinirSenha'
import { PaginaEntrar } from '../pages/entrar/PaginaEntrar'
import { PaginaNaoEncontrada } from '../pages/nao-encontrada/PaginaNaoEncontrada'
import { LayoutPublico } from '../pages/publico/LayoutPublico'
import { PaginaInicial } from '../pages/publico/inicio/PaginaInicial'
import { PaginaRecuperarSenha } from '../pages/recuperar-senha/PaginaRecuperarSenha'
import { RotaProtegida } from './RotaProtegida'
import { servicoDaCidade, servicoDeAutenticacao, servicoDeContribuicoes } from './servicos'
import { SoParaGestao } from './SoParaGestao'
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
      {
        element: <LayoutPublico />,
        children: [
          { index: true, element: <PaginaInicial /> },
          {
            path: 'como-funciona',
            lazy: async () => ({
              Component: (await import('../pages/publico/como-funciona/PaginaComoFunciona'))
                .PaginaComoFunciona,
            }),
          },
          {
            path: 'a-cidade-em-numeros',
            lazy: async () => ({
              Component: (
                await import('../pages/publico/a-cidade-em-numeros/PaginaCidadeEmNumeros')
              ).PaginaCidadeEmNumeros,
            }),
          },
          { path: 'o-que-muda', element: <Navigate to="/a-cidade-em-numeros" replace /> },
          { path: 'plataforma', element: <Navigate to="/como-funciona" replace /> },
          { path: 'dados-e-confianca', element: <Navigate to="/como-funciona" replace /> },
          {
            path: 'contribuir',
            lazy: async () => ({
              Component: (await import('../pages/publico/contribuir/PaginaContribuir'))
                .PaginaContribuir,
            }),
          },
        ],
      },
      {
        element: <SoParaVisitantes />,
        children: [
          { path: 'entrar', element: <PaginaEntrar area="cidade" /> },
          { path: 'entrar/gestao', element: <PaginaEntrar area="gestao" /> },
          { path: 'cadastrar', element: <PaginaCadastrar /> },
          { path: 'confirmar-email', element: <PaginaConfirmarEmail /> },
        ],
      },
      { path: 'entrar/ajuda', element: <PaginaAjudaDeAcesso /> },
      { path: 'recuperar-senha', element: <PaginaRecuperarSenha /> },
      {
        element: <RotaProtegida />,
        children: [
          { path: 'definir-senha', element: <PaginaDefinirSenha /> },
          {
            path: 'cidade',
            element: (
              <ContextoDaCidade value={servicoDaCidade}>
                <LayoutDaCidade />
              </ContextoDaCidade>
            ),
            children: [
              {
                index: true,
                lazy: async () => ({
                  Component: (await import('../pages/cidade/PaginaRelatosDaCidade'))
                    .PaginaRelatosDaCidade,
                }),
              },
              {
                path: 'meu-bairro',
                lazy: async () => ({
                  Component: (await import('../pages/cidade/PaginaMeuBairro')).PaginaMeuBairro,
                }),
              },
              {
                path: 'relatar',
                lazy: async () => ({
                  Component: (await import('../pages/cidade/PaginaRelatarNaCidade'))
                    .PaginaRelatarNaCidade,
                }),
              },
              {
                path: 'conta',
                lazy: async () => ({
                  Component: (await import('../pages/cidade/PaginaMinhaConta')).PaginaMinhaConta,
                }),
              },
            ],
          },
          {
            path: 'painel',
            element: <SoParaGestao />,
            children: [
              {
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
                      Component: (await import('../pages/painel/war-room/PaginaWarRoom'))
                        .PaginaWarRoom,
                    }),
                  },
                  {
                    path: 'retorno',
                    lazy: async () => ({
                      Component: (await import('../pages/painel/retorno/PaginaRetorno'))
                        .PaginaRetorno,
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
                      Component: (await import('../pages/importacoes/PaginaHistorico'))
                        .PaginaHistorico,
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
