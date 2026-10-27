export interface NumeroDoDataset {
  valor: string
  rotulo: string
}

export interface Achado {
  destaque: string
  afirmacao: string
  contexto: string
  fonte: string
}

export interface FonteDeDados {
  nome: string
  registra: string
  periodo: string
  registros: number
}

export interface Porta {
  nome: string
  registra: string
}

export const NUMEROS_DO_DATASET: readonly NumeroDoDataset[] = [
  { valor: '2.643.481', rotulo: 'registros reunidos' },
  { valor: '5', rotulo: 'fontes públicas' },
  { valor: '94', rotulo: 'bairros oficiais' },
  { valor: '2012 a 2026', rotulo: 'período coberto' },
]

export const NOTA_DO_DATASET =
  'Dataset RecifeView 1.0, de 13/10/2026, montado a partir do Portal de Dados Abertos do Recife, do sistema SAGL da Câmara Municipal e do Censo 2022 do IBGE.'

export const PORTAS: readonly Porta[] = [
  { nome: 'Central 156 / Emlurb', registra: 'pedidos de serviço urbano' },
  { nome: 'Ouvidoria-Geral', registra: 'reclamações e denúncias' },
  { nome: 'Defesa Civil', registra: 'vistorias, lonas e monitoramento' },
  { nome: 'SEDEC', registra: 'chamados em área de risco' },
  { nome: 'Câmara Municipal', registra: 'indicações de vereadores' },
]

export const ACHADOS: readonly Achado[] = [
  {
    destaque: '21%',
    afirmacao: 'das indicações da Câmara têm resposta registrada da Prefeitura.',
    contexto:
      'Quase todas chegam à Prefeitura (97%), mas, quando a resposta aparece, ela vem em mediana 241 dias depois. Sem resposta registrada não quer dizer que o pedido não foi atendido.',
    fonte: 'SAGL da Câmara Municipal do Recife, indicações de 2021 a 2025.',
  },
  {
    destaque: '53%',
    afirmacao:
      'dos pedidos ao 156 com endereço completo caem num local e serviço que já tinham pedido antes.',
    contexto:
      'Em 64% dessas repetições o pedido novo vem 30 dias ou mais depois: é reincidência, não duplicidade.',
    fonte:
      'Central 156/Emlurb, 2015 a 2025, só pedidos com número no endereço, repetição medida por local e serviço.',
  },
  {
    destaque: '55 a 87 dias',
    afirmacao: 'é o prazo dos 10% de pedidos mais demorados do 156, entre 2021 e 2024.',
    contexto:
      'Entre 2015 e 2020, eram 29 a 52 dias. A mediana ficou entre 3 e 7 dias: a demora cresceu na cauda, não no meio.',
    fonte: 'Central 156/Emlurb, percentil 90 do tempo até a última movimentação, por ano.',
  },
  {
    destaque: '38% a 75%',
    afirmacao:
      'é a parte que o órgão principal recebe das indicações de pavimentação, escadarias, praças e áreas de risco.',
    contexto:
      'O resto se espalha por outros órgãos. Em manutenção é diferente: cerca de 90% vai para a Emlurb.',
    fonte:
      'SAGL da Câmara Municipal do Recife, 2021 a 2025, categoria e órgão inferidos pelo texto da indicação.',
  },
]

export const NOTA_DOS_ACHADOS =
  'Resultados da análise exploratória do grupo (entrega N3, 23/10/2026). No painel, cada número será recalculado e poderá ser filtrado por bairro, serviço e período.'

export const PERGUNTAS_DA_GESTAO: readonly string[] = [
  'Por que esse local aparece tantas vezes?',
  'Essa concentração é recente?',
  'Quais regiões apresentam maior demora?',
]

export const FONTES_DE_DADOS: readonly FonteDeDados[] = [
  {
    nome: 'Central 156 / Emlurb',
    registra: 'Solicitação de serviço urbano',
    periodo: '2012 a 2026',
    registros: 1377158,
  },
  {
    nome: 'Defesa Civil',
    registra: 'Ação da Defesa Civil (vistoria, lona, monitoramento)',
    periodo: '2014 a 2024',
    registros: 886263,
  },
  {
    nome: 'Ouvidoria-Geral',
    registra: 'Manifestação do cidadão',
    periodo: '2018 a 2025',
    registros: 222855,
  },
  {
    nome: 'SEDEC',
    registra: 'Chamado em área de risco',
    periodo: '2012 a 2024',
    registros: 90659,
  },
  {
    nome: 'Câmara Municipal',
    registra: 'Indicação ou requerimento de vereador',
    periodo: '2021 a 2025',
    registros: 66546,
  },
]

export const EQUIPE: readonly string[] = [
  'Davi Santiago',
  'Gustavo Henrique Cruz de Oliveira',
  'Henrique Sérgio C. de Brito',
  'João Pedro R. Dornelas de Araujo',
  'Lucas Ramon',
  'Lucas Rodrigues Campos',
  'Mateus de Almeida Ribeiro',
]

export const LINKS_DO_PROJETO = {
  desafio: 'https://inovacaoaberta.recife.pe.gov.br/',
  site: 'https://sites.google.com/cesar.school/recifeview/início',
  codigo: 'https://github.com/Mateus-Ribeir0/RecifeView',
} as const
