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

export interface Razao {
  icone: NomeDoIcone
  antes: string
  agora: string
}

export interface Passo {
  icone: NomeDoIcone
  titulo: string
  texto: string
}

export interface LinhaDeAcesso {
  recurso: string
  semConta: boolean
  cidadao: boolean
  gestao: boolean
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

export const RAZOES_PARA_RELATAR: readonly Razao[] = [
  {
    icone: 'relogio',
    antes: 'Você relatava um problema e não sabia mais o que tinha acontecido com ele.',
    agora:
      'Cada relato mostra em que pé está: recebido, em análise, no painel da gestão ou já com pedido oficial.',
  },
  {
    icone: 'somar',
    antes: 'O mesmo buraco virava dez pedidos soltos, e nenhum parecia mais urgente.',
    agora:
      'Relatos iguais viram uma ocorrência só. Cada pessoa a mais que relata reforça o mesmo problema.',
  },
  {
    icone: 'local',
    antes: 'Ninguém fora da Prefeitura via o que se repetia no bairro.',
    agora:
      'Você vê os relatos da sua rua e do seu bairro, e como o bairro se compara com o Recife.',
  },
  {
    icone: 'escudo',
    antes: 'Relatar parecia expor o próprio endereço.',
    agora:
      'Ninguém vê o número exato, o que você escreveu nem quem enviou. O relato não pede seus dados.',
  },
]

export const PASSOS_DO_CIDADAO: readonly Passo[] = [
  {
    icone: 'relato',
    titulo: 'Você relata',
    texto: 'Escolhe o problema e a rua. Leva um minuto e não precisa de conta.',
  },
  {
    icone: 'somar',
    titulo: 'A plataforma confere',
    texto: 'Se outra pessoa já relatou o mesmo problema, os relatos viram uma ocorrência só.',
  },
  {
    icone: 'pessoas',
    titulo: 'A gestão revisa',
    texto: 'Uma pessoa da gestão confere os casos parecidos antes de o relato entrar nos números.',
  },
  {
    icone: 'telas',
    titulo: 'Você acompanha',
    texto: 'Com uma conta, você acompanha cada relato seu em Meus relatos e vê o seu bairro.',
  },
]

export const NIVEIS_DE_ACESSO: readonly LinhaDeAcesso[] = [
  {
    recurso: 'Números da cidade, a partir dos dados abertos',
    semConta: true,
    cidadao: true,
    gestao: true,
  },
  { recurso: 'Relatar um problema', semConta: true, cidadao: true, gestao: true },
  {
    recurso: 'Relatos da cidade: rua, faixa de numeração, situação e quantas pessoas relataram',
    semConta: false,
    cidadao: true,
    gestao: true,
  },
  {
    recurso: 'Os seus relatos e o andamento de cada um, do envio à revisão',
    semConta: false,
    cidadao: true,
    gestao: false,
  },
  {
    recurso: 'Indicadores do seu bairro comparados com o Recife',
    semConta: false,
    cidadao: true,
    gestao: true,
  },
  {
    recurso: 'Número exato e texto escrito do relato, para conferir duplicidade',
    semConta: false,
    cidadao: false,
    gestao: true,
  },
  {
    recurso: 'Painel da gestão, prioridade, importação de arquivos e pente fino',
    semConta: false,
    cidadao: false,
    gestao: true,
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
  'O relato não pede nome, CPF, telefone nem e-mail e recusa o texto que trouxer esses dados.',
  'Com a conta aberta, o relato aparece em Meus relatos só para você. A gestão revisa sem saber quem enviou, e relato feito sem entrar não fica ligado a ninguém.',
  'A conta guarda só nome, e-mail e, se você quiser, o bairro. Excluir a conta apaga esses dados.',
  'Quem tem conta vê a rua e uma faixa de numeração de 100 em 100, nunca o número exato nem o texto escrito.',
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
  'Um relato no formulário não é um pedido oficial: para ter protocolo, use a Central 156.',
]
