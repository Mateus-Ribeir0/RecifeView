import type { NomeDoIcone } from '../components/Icone'

export type FiltroDaTela = 'periodo' | 'rpa' | 'bairro' | 'categoria'

export interface TelaDoPainel {
  nome: string
  caminho: string
  mostra: string
  icone: NomeDoIcone
  filtros: readonly FiltroDaTela[]
}

export interface GrupoDeTelas {
  grupo: string
  telas: readonly TelaDoPainel[]
}

const TODOS_OS_FILTROS: readonly FiltroDaTela[] = ['periodo', 'rpa', 'bairro', 'categoria']
const SEM_FILTROS: readonly FiltroDaTela[] = []

export const ROTA_RAIZ_DO_PAINEL = '/painel'

export const GRUPOS_DE_TELAS: readonly GrupoDeTelas[] = [
  {
    grupo: 'Visão geral',
    telas: [
      {
        nome: 'Início',
        caminho: ROTA_RAIZ_DO_PAINEL,
        mostra: 'Os principais indicadores e o volume por fonte.',
        icone: 'inicio',
        filtros: TODOS_OS_FILTROS,
      },
      {
        nome: 'War Room',
        caminho: '/painel/war-room',
        mostra: 'O estado de um dia: o que está parado e por onde começar.',
        icone: 'pulso',
        filtros: SEM_FILTROS,
      },
    ],
  },
  {
    grupo: 'Onde o pedido se perde',
    telas: [
      {
        nome: 'Retorno',
        caminho: '/painel/retorno',
        mostra: 'Para onde vai cada tipo de pedido e quanto volta.',
        icone: 'retorno',
        filtros: TODOS_OS_FILTROS,
      },
      {
        nome: 'Reincidência',
        caminho: '/painel/reincidencia',
        mostra: 'Repetir não é duplicar: o problema volta.',
        icone: 'repetir',
        filtros: TODOS_OS_FILTROS,
      },
      {
        nome: 'Prazos',
        caminho: '/painel/prazos',
        mostra: 'Quem demora está demorando mais.',
        icone: 'relogio',
        filtros: TODOS_OS_FILTROS,
      },
    ],
  },
  {
    grupo: 'Onde agir primeiro',
    telas: [
      {
        nome: 'Território',
        caminho: '/painel/territorio',
        mostra: 'Serviço urbano e emergência apontam para bairros diferentes.',
        icone: 'local',
        filtros: TODOS_OS_FILTROS,
      },
      {
        nome: 'Prioridade',
        caminho: '/painel/prioridade',
        mostra: 'Um índice com critérios explícitos e ajustáveis.',
        icone: 'bandeira',
        filtros: ['rpa', 'bairro', 'categoria'],
      },
    ],
  },
  {
    grupo: 'Dados',
    telas: [
      {
        nome: 'Importações',
        caminho: '/painel/importacoes',
        mostra: 'Enviar arquivos novos e ver o histórico do que entrou na base.',
        icone: 'importar',
        filtros: SEM_FILTROS,
      },
      {
        nome: 'Sobre os dados',
        caminho: '/painel/sobre-os-dados',
        mostra: 'Fontes, cobertura, cuidados, correções e privacidade.',
        icone: 'informacao',
        filtros: SEM_FILTROS,
      },
    ],
  },
]

export const TELAS_DO_PAINEL: readonly TelaDoPainel[] = GRUPOS_DE_TELAS.flatMap(
  (grupo) => grupo.telas,
)

export function filtrosDaRota(caminho: string): readonly FiltroDaTela[] {
  return TELAS_DO_PAINEL.find((tela) => tela.caminho === caminho)?.filtros ?? SEM_FILTROS
}
