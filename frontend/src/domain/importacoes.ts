import { nomeDaFonte } from './fontes'
import { contar } from './formatacao'

export type StatusDaImportacao =
  | 'ANALISANDO'
  | 'AGUARDANDO_COLUNAS'
  | 'VALIDANDO'
  | 'AGUARDANDO_DECISOES'
  | 'PRONTA'
  | 'CARREGANDO'
  | 'ATUALIZANDO_PAINEL'
  | 'CONCLUIDA'
  | 'FALHOU'
  | 'CANCELADA'
  | 'DESFAZENDO'
  | 'DESFEITA'

export type TipoDePendencia =
  | 'formato_de_data'
  | 'bairro_desconhecido'
  | 'valor_novo'
  | 'datas_invalidas'
  | 'repetidos_na_base'
  | 'repetidos_no_arquivo'
  | 'coincidencias_certas'
  | 'coincidencias_provaveis'

export const DEIXAR_VAZIO = '__deixar_vazio__'
export const DESCARTAR_LINHA = '__descartar_linha__'
export const ACEITAR_COMO_NOVO = '__aceitar_como_novo__'

const STATUS_EM_PROCESSAMENTO: ReadonlySet<StatusDaImportacao> = new Set([
  'ANALISANDO',
  'VALIDANDO',
  'CARREGANDO',
  'ATUALIZANDO_PAINEL',
  'DESFAZENDO',
])

const STATUS_ENCERRADOS: ReadonlySet<StatusDaImportacao> = new Set([
  'CONCLUIDA',
  'FALHOU',
  'CANCELADA',
  'DESFEITA',
])

export const ROTULOS_DOS_STATUS: Readonly<Record<StatusDaImportacao, string>> = {
  ANALISANDO: 'Lendo o arquivo',
  AGUARDANDO_COLUNAS: 'Aguardando as colunas',
  VALIDANDO: 'Conferindo os dados',
  AGUARDANDO_DECISOES: 'Aguardando decisões',
  PRONTA: 'Pronta para carregar',
  CARREGANDO: 'Gravando na base',
  ATUALIZANDO_PAINEL: 'Atualizando o painel',
  CONCLUIDA: 'Concluída',
  FALHOU: 'Falhou',
  CANCELADA: 'Cancelada',
  DESFAZENDO: 'Desfazendo',
  DESFEITA: 'Desfeita',
}

export const ROTULOS_DOS_DESCARTES: Readonly<Record<string, string>> = {
  linha_quebrada: 'Linhas quebradas',
  sem_data_de_abertura: 'Sem data de abertura',
  data_invalida: 'Com data inválida',
  dado_pessoal: 'Com dado pessoal',
  valor_recusado: 'Recusadas nas decisões',
  repetida_no_arquivo: 'Repetidas no arquivo',
}

export const ROTULOS_DAS_CORRECOES: Readonly<Record<string, string>> = {
  prazo_negativo: 'Prazos negativos anulados',
  categoria_unificada: '156: categorias unificadas (terraplenagem)',
  orgao_harmonizado: 'Ouvidoria: nomes de órgão harmonizados',
  bairro_recuperado: 'Câmara: bairro recuperado pela ementa',
  rpa_preenchida: 'RPA preenchida pelo bairro',
  bairro_associado: 'Bairros associados nas decisões',
  fechado_no_dia: '156: pedidos fechados no mesmo dia (marcados)',
}

export function estaEmProcessamento(status: StatusDaImportacao): boolean {
  return STATUS_EM_PROCESSAMENTO.has(status)
}

export function estaEncerrada(status: StatusDaImportacao): boolean {
  return STATUS_ENCERRADOS.has(status)
}

export interface ColunaDoArquivo {
  nome: string
  campo: string | null
  origem: string
  bloqueada: boolean
  motivoDeBloqueio: string | null
  exemplos: readonly string[]
}

export interface ValorEmDuvida {
  valor: string
  quantidade: number
  sugestao: string | null
}

export interface Pendencia {
  tipo: TipoDePendencia
  campo: string | null
  rotuloDoCampo: string | null
  quantidade: number
  valores: readonly ValorEmDuvida[]
  alternativas: readonly string[]
  totalDeValores: number
  detalhes: Readonly<Record<string, number>>
}

export interface PenteFino {
  comparadas: number
  semEndereco: number
  certas: number
  provaveis: number
}

export interface ResumoDaValidacao {
  lidas: number
  aceitas: number
  novas: number
  iguais: number
  alteradas: number
  repetidasNoArquivo: number
  semIdLocal: number
  periodoInicio: string | null
  periodoFim: string | null
  descartes: Readonly<Record<string, number>>
  correcoes: Readonly<Record<string, number>>
  fontes: Readonly<Record<string, number>>
  penteFino: Partial<PenteFino>
}

export interface ResultadoDaCarga {
  lidas: number
  aceitas: number
  novas: number
  atualizadas: number
  iguais: number
  ignoradas: number
  retiradas: number
  repetidasNoArquivo: number
  semIdLocal: number
  descartes: Readonly<Record<string, number>>
  correcoes: Readonly<Record<string, number>>
  fontes: Readonly<Record<string, number>>
  penteFino: Partial<PenteFino>
}

export interface PreviaDeLinha {
  antes: Readonly<Record<string, string>>
  depois: Readonly<Record<string, string>>
}

export interface ResumoDaImportacao {
  id: number
  nomeDoArquivo: string
  tamanhoEmBytes: number
  status: StatusDaImportacao
  progresso: number
  fonte: string | null
  layout: string | null
  dataDoRetrato: string | null
  periodoInicio: string | null
  periodoFim: string | null
  criadaEm: string
  concluidaEm: string | null
  desfeitaEm: string | null
  nomeDeQuemImportou: string | null
  cargaInicial: boolean
  arquivoGuardado: boolean
  resultado: ResultadoDaCarga
}

export interface DecisoesDaImportacao {
  fonte: string | null
  dataDoRetrato: string | null
  mapeamento: Readonly<Record<string, string>>
  valoresFixos: Readonly<Record<string, string>>
  formatoDeData: string | null
  substituicoes: Readonly<Record<string, Readonly<Record<string, string>>>>
  padraoParaValores: Readonly<Record<string, string>>
  datasInvalidas: string | null
  repetidosNaBase: string | null
  repetidosNoArquivo: string | null
  coincidenciasCertas: string | null
  coincidenciasProvaveis: string | null
}

export interface DetalheDaImportacao extends ResumoDaImportacao {
  estrutura: {
    formato: string | null
    codificacao: string | null
    separador: string | null
    layoutNome: string | null
    guardarArquivo: boolean | null
    colunas: readonly ColunaDoArquivo[]
    mesmoArquivo: readonly { id: number; criadaEm: string; status: string }[]
  }
  decisoes: DecisoesDaImportacao
  pendencias: {
    itens: readonly Pendencia[]
    resumo: ResumoDaValidacao
    previa: readonly PreviaDeLinha[]
  }
  mensagemDeErro: string | null
  podeDesfazer: boolean
}

export interface CampoDaBase {
  nome: string
  rotulo: string
  tipo: string
  descricao: string
}

export interface EscolhaDeColunas {
  fonte: string | null
  dataDoRetrato: string
  mapeamento: Readonly<Record<string, string | null>>
  valoresFixos: Readonly<Record<string, string>>
}

export interface RespostasDePendencias {
  formatoDeData?: string
  substituicoes?: Readonly<Record<string, Readonly<Record<string, string>>>>
  padraoParaValores?: Readonly<Record<string, string>>
  datasInvalidas?: string
  repetidosNaBase?: string
  repetidosNoArquivo?: string
  coincidenciasCertas?: string
  coincidenciasProvaveis?: string
}

export interface FiltroDoHistorico {
  busca: string
  situacao: string
  deslocamento: number
}

export interface PaginaDeImportacoes {
  itens: readonly ResumoDaImportacao[]
  total: number
}

export interface RegistroImportado {
  fonte: string
  ano: number | null
  dataAbertura: string | null
  dataUltMovimento: string | null
  diasAteMovimento: number | null
  categoria: string | null
  servico: string | null
  orgao: string | null
  bairroOficial: string | null
  rpa: string | null
  situacao: string | null
}

export interface PaginaDeRegistros {
  itens: readonly RegistroImportado[]
  total: number
}

const LAYOUT_COM_VARIAS_FONTES = 'dataset'

export function descreverFonte({
  fonte,
  layout,
}: Pick<ResumoDaImportacao, 'fonte' | 'layout'>): string {
  if (fonte || layout === LAYOUT_COM_VARIAS_FONTES) return nomeDaFonte(fonte)
  return 'fonte a definir'
}

const ROTULOS_DAS_ESCOLHAS: Readonly<Record<string, string>> = {
  atualizar: 'atualizar',
  manter_atuais: 'manter os atuais',
  inserir_como_novos: 'inserir como novos',
  manter_todos: 'manter todos',
  manter_um: 'manter só um de cada',
  manter_o_registro_oficial: 'manter o registro oficial e retirar o relato',
  manter_os_dois: 'manter os dois',
  deixar_vazia: 'deixar vazia',
  descartar_linha: 'descartar a linha',
  iso: 'ano-mês-dia',
  ano_barra: 'ano/mês/dia',
  dia_mes_ano: 'dia/mês/ano',
  mes_dia_ano: 'mês/dia/ano',
}

const ROTULOS_DOS_CAMPOS_DECIDIDOS: Readonly<Record<string, string>> = {
  bairro: 'Bairro',
  categoria: 'Categoria',
  orgao: 'Órgão',
  situacao: 'Situação',
}

function descreverEscolha(titulo: string, escolha: string | null): string[] {
  return escolha ? [`${titulo}: ${ROTULOS_DAS_ESCOLHAS[escolha] ?? escolha}`] : []
}

export function descreverDecisoes(decisoes: DecisoesDaImportacao): string[] {
  const valores = Object.entries(decisoes.substituicoes).flatMap(([campo, substituicoes]) => {
    const quantidade = Object.keys(substituicoes).length
    if (quantidade === 0) return []
    const rotulo = ROTULOS_DOS_CAMPOS_DECIDIDOS[campo] ?? campo
    return [`${rotulo}: ${contar(quantidade, 'valor decidido', 'valores decididos')}`]
  })
  return [
    ...descreverEscolha('Registros já na base', decisoes.repetidosNaBase),
    ...descreverEscolha('Repetidos no arquivo', decisoes.repetidosNoArquivo),
    ...descreverEscolha('Mesma demanda no formulário', decisoes.coincidenciasCertas),
    ...descreverEscolha('Provável demanda no formulário', decisoes.coincidenciasProvaveis),
    ...descreverEscolha('Datas inválidas', decisoes.datasInvalidas),
    ...descreverEscolha('Ordem das datas', decisoes.formatoDeData),
    ...valores,
  ]
}
