export interface TelaDoPainel {
  nome: string
  caminho: string
  mostra: string
}

export interface GrupoDeTelas {
  grupo: string
  telas: readonly TelaDoPainel[]
}

export const GRUPOS_DE_TELAS: readonly GrupoDeTelas[] = [
  {
    grupo: 'Visão geral',
    telas: [
      {
        nome: 'Início',
        caminho: '/painel',
        mostra: 'Os principais indicadores e o volume por fonte.',
      },
      {
        nome: 'War Room',
        caminho: '/painel/war-room',
        mostra: 'O estado de um dia: o que está parado e por onde começar.',
      },
    ],
  },
  {
    grupo: 'Onde o pedido se perde',
    telas: [
      {
        nome: 'Retorno e fragmentação',
        caminho: '/painel/retorno',
        mostra: 'Para onde vai cada tipo de pedido e quanto volta.',
      },
      {
        nome: 'Reincidência',
        caminho: '/painel/reincidencia',
        mostra: 'Repetir não é duplicar: o problema volta.',
      },
      { nome: 'Prazos', caminho: '/painel/prazos', mostra: 'Quem demora está demorando mais.' },
    ],
  },
  {
    grupo: 'Onde agir primeiro',
    telas: [
      {
        nome: 'Território',
        caminho: '/painel/territorio',
        mostra: 'Serviço urbano e emergência apontam para bairros diferentes.',
      },
      {
        nome: 'Prioridade (AHP)',
        caminho: '/painel/prioridade',
        mostra: 'Um índice com critérios explícitos e ajustáveis.',
      },
    ],
  },
  {
    grupo: 'Referência',
    telas: [
      {
        nome: 'Sobre os dados',
        caminho: '/painel/sobre-os-dados',
        mostra: 'Fontes, cobertura, cuidados, correções e privacidade.',
      },
    ],
  },
]

export const TELAS_DO_PAINEL: readonly TelaDoPainel[] = GRUPOS_DE_TELAS.flatMap(
  (grupo) => grupo.telas,
)
