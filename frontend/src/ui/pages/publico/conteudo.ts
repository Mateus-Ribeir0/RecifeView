import type { NomeDoIcone } from '../../components/Icone'

export interface NumeroDaBase {
  valor: number
  rotulo: string
}

export interface FonteDeDados {
  nome: string
  registra: string
  periodo: string
  registros: number
  cor: string
}

export interface ProblemaResolvido {
  chave: string
  icone: NomeDoIcone
  titulo: string
  antes: string
  agora: string
  tela: string
  caminho: string
}

export interface ResultadoPedido {
  pedido: string
  resposta: string
}

export interface TelaDaPlataforma {
  chave: string
  nome: string
  icone: NomeDoIcone
  pergunta: string
  permite: readonly string[]
}

export interface CamadaDoPenteFino {
  icone: NomeDoIcone
  titulo: string
  texto: string
}

export const NUMEROS_DA_BASE: readonly NumeroDaBase[] = [
  { valor: 2643481, rotulo: 'registros reunidos' },
  { valor: 5, rotulo: 'fontes públicas numa leitura só' },
  { valor: 94, rotulo: 'bairros oficiais' },
  { valor: 15, rotulo: 'anos de histórico, de 2012 a 2026' },
]

export const NOTA_DA_BASE =
  'Fonte: Portal de Dados Abertos do Recife, SAGL da Câmara Municipal e Censo 2022 do IBGE. Base de 07/10/2026.'

export const PROBLEMAS: readonly ProblemaResolvido[] = [
  {
    chave: 'fragmentacao',
    icone: 'base',
    titulo: 'Cada porta guardava a sua base',
    antes:
      'Central 156, Ouvidoria, Defesa Civil, SEDEC e Câmara Municipal registram em sistemas separados, sem um identificador em comum. Ver o todo significava juntar planilhas na mão.',
    agora:
      'As cinco fontes estão numa base única e se cruzam por bairro, serviço e período. Um filtro aplicado vale para todas as telas.',
    tela: 'Início',
    caminho: '/plataforma',
  },
  {
    chave: 'repeticao',
    icone: 'repetir',
    titulo: 'A repetição parecia só mais um pedido',
    antes:
      'Vista sozinha, uma solicitação repetida não chamava atenção. O problema voltava ao mesmo endereço e ninguém enxergava o padrão.',
    agora:
      'A Reincidência separa o pedido duplicado, de até 7 dias, do problema que volta, de 30 dias ou mais, e aponta os pontos crônicos de cada bairro.',
    tela: 'Reincidência',
    caminho: '/plataforma',
  },
  {
    chave: 'retorno',
    icone: 'retorno',
    titulo: 'O retorno se perdia no caminho',
    antes:
      'A indicação chegava à Prefeitura, mas a resposta raramente voltava ao registro. Não dava para ver em que etapa ela parava.',
    agora:
      'O funil do Retorno mostra o que foi apresentado, enviado e respondido, com o canal e o órgão de cada etapa.',
    tela: 'Retorno',
    caminho: '/plataforma',
  },
  {
    chave: 'prazos',
    icone: 'relogio',
    titulo: 'A mediana escondia a demora',
    antes:
      'A mediana do 156 ficou entre 2 e 5 dias, o que passava a impressão de um serviço estável. Os pedidos mais demorados não apareciam.',
    agora:
      'Os Prazos mostram mediana e percentil 90 por ano e categoria, além do estoque que já passou do prazo típico.',
    tela: 'Prazos',
    caminho: '/plataforma',
  },
  {
    chave: 'destino',
    icone: 'filtro',
    titulo: 'Ninguém via para onde cada tema ia',
    antes:
      'Risco, escadarias, praças e pavimentação se espalham por vários órgãos. Não havia uma visão de quem recebe o quê.',
    agora:
      'O mapa de calor e o fluxo de categoria para órgão mostram onde o encaminhamento muda de mão.',
    tela: 'Retorno',
    caminho: '/plataforma',
  },
  {
    chave: 'prioridade',
    icone: 'bandeira',
    titulo: 'Priorizar dependia de quem olhava',
    antes:
      'Sem critério escrito, a fila seguia a ordem de chegada ou a pressão do momento, e mais pedidos num bairro nem sempre queria dizer mais problema.',
    agora:
      'A Prioridade usa quatro critérios escritos (risco, vulnerabilidade, atraso e reincidência), com pesos que a gestão ajusta, e a War Room mostra por onde começar.',
    tela: 'Prioridade e War Room',
    caminho: '/plataforma',
  },
  {
    chave: 'importacao',
    icone: 'importar',
    titulo: 'Arquivo novo dava trabalho e podia duplicar',
    antes:
      'Cada arquivo dependia de quem sabia rodar os scripts, e nada impedia a mesma demanda de entrar duas vezes por canais diferentes.',
    agora:
      'A Importação pergunta o que não bateu, passa o pente fino entre os canais, guarda o histórico e permite desfazer. Nada entra com pendência aberta.',
    tela: 'Importações',
    caminho: '/dados-e-confianca',
  },
]

export const RESUMO_DO_QUE_MUDA: readonly string[] = [
  'repeticao',
  'retorno',
  'prazos',
  'importacao',
]

export const RESULTADOS_PEDIDOS: readonly ResultadoPedido[] = [
  {
    pedido: 'Classificação mais precisa e consistente',
    resposta:
      'Um vocabulário só de serviço, categoria e bairro oficial para todas as fontes, com as grafias e os órgãos harmonizados na entrada.',
  },
  {
    pedido: 'Priorização por criticidade, impacto e recorrência',
    resposta:
      'Índice por bairro com critérios explícitos, fila de ocorrências com nota e reincidência calculada por local e serviço.',
  },
  {
    pedido: 'Menos tempo até o encaminhamento adequado',
    resposta:
      'Funil, fluxo entre órgãos e estoque fora do prazo mostram em que etapa a demanda para, para a gestão agir ali.',
  },
  {
    pedido: 'Uso estratégico para achar gargalos urbanos',
    resposta:
      'Taxas por mil habitantes, pontos crônicos e dois mapas (serviço urbano e emergência), porque os dois apontam para bairros diferentes.',
  },
]

export const TELAS_DA_PLATAFORMA: readonly TelaDaPlataforma[] = [
  {
    chave: 'inicio',
    nome: 'Início',
    icone: 'inicio',
    pergunta: 'Como está a demanda do Recife, em uma tela?',
    permite: [
      'Ver os principais indicadores e o volume que chega por cada porta',
      'Filtrar por período, RPA, bairro e categoria, com efeito em todas as telas',
      'Abrir o mapa de concentração por mil habitantes',
    ],
  },
  {
    chave: 'war-room',
    nome: 'War Room',
    icone: 'pulso',
    pergunta: 'O que está parado hoje e por onde começar?',
    permite: [
      'Acompanhar o estoque aberto, o que passou do prazo típico e as indicações sem resposta',
      'Ver a fila do dia ordenada por nota, com bairro, serviço e tempo em aberto',
      'Simular um mês para ensaiar a rotina da sala de situação',
    ],
  },
  {
    chave: 'retorno',
    nome: 'Retorno',
    icone: 'retorno',
    pergunta: 'Para onde vai cada pedido e quanto volta?',
    permite: [
      'Seguir o funil da Câmara: apresentada, enviada e com resposta',
      'Comparar canais de envio e ver o que muda na resposta',
      'Ler o fluxo de categoria para órgão e os canais da Ouvidoria',
    ],
  },
  {
    chave: 'reincidencia',
    nome: 'Reincidência',
    icone: 'repetir',
    pergunta: 'O problema foi resolvido ou voltou?',
    permite: [
      'Medir o percentual de pedidos em local e serviço já pedidos antes',
      'Separar duplicidade (até 7 dias) de reincidência (30 dias ou mais)',
      'Listar os pontos crônicos, sem expor o endereço',
    ],
  },
  {
    chave: 'prazos',
    nome: 'Prazos',
    icone: 'relogio',
    pergunta: 'Quem demora está demorando mais?',
    permite: [
      'Comparar mediana e percentil 90 por ano e por categoria',
      'Encontrar o estoque aberto além do prazo típico de cada serviço',
      'Tirar da conta os pedidos fechados no mesmo dia',
    ],
  },
  {
    chave: 'territorio',
    nome: 'Território',
    icone: 'local',
    pergunta: 'Onde o serviço urbano e a emergência pesam mais?',
    permite: [
      'Comparar dois mapas com taxa por mil habitantes',
      'Clicar num bairro e ver o detalhe nas duas leituras',
      'Conferir tudo na tabela ordenada ao lado do mapa',
    ],
  },
  {
    chave: 'prioridade',
    nome: 'Prioridade',
    icone: 'bandeira',
    pergunta: 'Com critérios escritos, onde agir primeiro?',
    permite: [
      'Ajustar os pesos dos quatro critérios e ver o ranking mudar',
      'Conferir a consistência dos julgamentos e a sensibilidade do índice',
      'Abrir a fila de ocorrências classificadas',
    ],
  },
  {
    chave: 'contribuicoes',
    nome: 'Contribuições',
    icone: 'relato',
    pergunta: 'O que chegou pelo formulário e já pode entrar na base?',
    permite: [
      'Revisar lado a lado os relatos parecidos e decidir se são a mesma ocorrência',
      'Ver quantas pessoas relataram cada problema e quantas ficaram sem retorno',
      'Gerar o pacote que segue para a importação, com histórico e desfazer',
    ],
  },
]

export const CAMADAS_DO_PENTE_FINO: readonly CamadaDoPenteFino[] = [
  {
    icone: 'confirmado',
    titulo: 'Mesmo envio não conta duas vezes',
    texto:
      'Cada formulário tem uma chave própria. Um clique duplo ou uma conexão que caiu no meio não cria outro relato.',
  },
  {
    icone: 'via',
    titulo: 'O endereço é escrito como a fonte escreve',
    texto:
      '“R. do Sol” e “Rua do Sol” viram a mesma via, conferida na lista de ruas do bairro. Assim o relato fala a mesma língua do arquivo da Central 156.',
  },
  {
    icone: 'filtro',
    titulo: 'A comparação olha o que importa',
    texto:
      'Dentro do mesmo bairro e tema, a pontuação pesa o endereço, o serviço, o intervalo de tempo e o detalhe informado. Erro de digitação não engana.',
  },
  {
    icone: 'relogio',
    titulo: 'O tempo separa duplicidade de reincidência',
    texto:
      'Até 7 dias é duplicidade. De 8 a 29 dias, só uma pessoa decide. Com 30 dias ou mais, o problema voltou: essa informação é preciosa e nunca é apagada.',
  },
  {
    icone: 'pessoas',
    titulo: 'A dúvida fica com a gestão',
    texto:
      'Só o que é certo é somado sozinho. O resto aparece lado a lado, com o motivo escrito. Nenhum pacote sai com dupla sem decisão, e a carga pode ser desfeita.',
  },
]

export const FONTES_DE_DADOS: readonly FonteDeDados[] = [
  {
    nome: 'Central 156 / Emlurb',
    registra: 'Solicitação de serviço urbano',
    periodo: '2012 a 2026',
    registros: 1377158,
    cor: 'var(--cor-fonte-156)',
  },
  {
    nome: 'Defesa Civil',
    registra: 'Ação da Defesa Civil (vistoria, lona, monitoramento)',
    periodo: '2014 a 2024',
    registros: 886263,
    cor: 'var(--cor-fonte-defesa-civil)',
  },
  {
    nome: 'Ouvidoria-Geral',
    registra: 'Manifestação do cidadão',
    periodo: '2018 a 2025',
    registros: 222855,
    cor: 'var(--cor-fonte-ouvidoria)',
  },
  {
    nome: 'SEDEC',
    registra: 'Chamado em área de risco',
    periodo: '2012 a 2024',
    registros: 90659,
    cor: 'var(--cor-fonte-sedec)',
  },
  {
    nome: 'Câmara Municipal',
    registra: 'Indicação ou requerimento de vereador',
    periodo: '2021 a 2025',
    registros: 66546,
    cor: 'var(--cor-fonte-camara)',
  },
]

export const GARANTIAS_DE_PRIVACIDADE: readonly string[] = [
  'O formulário não pede nome, CPF, telefone nem e-mail, e recusa o texto que trouxer esses dados.',
  'O relato fica numa área separada. Só entra no painel depois da revisão da gestão.',
  'A base analítica nunca recebe endereço nem texto livre: só um código que não pode ser revertido sem um segredo guardado fora do sistema.',
  'Endereço e detalhe do relato são apagados em 90 dias.',
  'Nenhum relato é enviado a serviço externo. A comparação roda dentro da plataforma.',
  'O texto dos chamados em área de risco nunca sai da base.',
]

export const LEITURAS_HONESTAS: readonly string[] = [
  'Sem resposta registrada não quer dizer que o pedido não foi atendido.',
  'Mais pedidos num bairro não quer dizer mais problema: por isso o painel usa taxa por mil habitantes.',
  'A Defesa Civil registra ações, não pedidos, e a situação da SEDEC é um retrato de 03/2024.',
  'Os pesos do índice de prioridade são uma proposta inicial e podem ser mudados na tela.',
]
