import { formatarData, formatarNumero } from '../../../../domain/formatacao'
import { nomeDaCategoria, nomeDoOrgao } from '../../../../domain/nomes'
import type { FonteDaFila, OcorrenciaClassificada } from '../../../../domain/prioridade'

const SITUACOES: Readonly<Record<string, string>> = {
  CADASTRADA: 'cadastrado',
  PREPARACAO: 'em preparação',
  EXECUCAO: 'em execução',
  PENDENCIA: 'com pendência',
  FISCALIZACAO: 'em fiscalização',
  MONITORAMENTO: 'em monitoramento',
}
const CANAIS_DE_ENVIO: Readonly<Record<string, string>> = {
  OFICIO: 'ofício',
  'PROTOCOLO NA PREFEITURA': 'protocolo na Prefeitura',
  'LOTE JSON SISTEMA PCR': 'lote do sistema da Prefeitura',
  'SISTEMA SEGOV': 'sistema da SEGOV',
  'ENVIADO AO EXECUTIVO': 'envio ao Executivo',
  'E-MAIL': 'e-mail',
  'CIENCIA AOS INTERESSADOS': 'ciência aos interessados',
}

export interface TextosDaOcorrencia {
  titulo: string
  contexto: string
  tempo: string
  repeticao: string
}

function repeticaoDo156(anteriores: number | null): string {
  if (anteriores === null) return 'Endereço sem número: não dá para saber se o problema se repete.'
  if (anteriores === 0) return 'Primeiro pedido deste serviço no endereço.'
  const plural = anteriores > 1 ? 's' : ''
  return `O endereço já teve ${formatarNumero(anteriores)} pedido${plural} do mesmo serviço antes deste.`
}

function textosDo156(item: OcorrenciaClassificada, nome: string): TextosDaOcorrencia {
  const prazo = item.prazoTipicoDias
  const textoDoPrazo =
    prazo === null
      ? 'categoria sem prazo típico'
      : `prazo típico da categoria: ${formatarNumero(prazo)} dias (${formatarNumero(item.idadeDias / Math.max(prazo, 1), 1)}× o prazo)`
  return {
    titulo: nomeDaCategoria(item.servico),
    contexto: `${nomeDaCategoria(item.categoria)} · ${nome} (RPA ${item.rpa ?? 'não informada'}) · ${SITUACOES[item.situacao ?? ''] ?? (item.situacao ?? '').toLowerCase()}`,
    tempo: `Aberto em ${formatarData(item.dataAbertura)}, há ${formatarNumero(item.idadeDias)} dias; ${textoDoPrazo}.`,
    repeticao: repeticaoDo156(item.pedidosAnteriores),
  }
}

function textosDaCamara(item: OcorrenciaClassificada, nome: string): TextosDaOcorrencia {
  const anteriores = item.pedidosAnteriores ?? 0
  const prazo = item.prazoTipicoDias ?? 1
  const canal =
    CANAIS_DE_ENVIO[item.canal ?? ''] ?? (item.canal ?? 'canal não informado').toLowerCase()
  return {
    titulo: `Indicação: ${nomeDaCategoria(item.categoria).toLowerCase()}`,
    contexto: `${nome} (RPA ${item.rpa ?? 'não informada'}) · enviada a ${nomeDoOrgao(item.orgao)} por ${canal}`,
    tempo: `Apresentada em ${formatarData(item.dataAbertura)}, enviada em ${formatarData(item.dataEnvio)}: há ${formatarNumero(item.idadeDias)} dias sem resposta; tempo típico até a resposta no tema: ${formatarNumero(prazo)} dias (${formatarNumero(item.idadeDias / Math.max(prazo, 1), 1)}×).`,
    repeticao:
      anteriores === 0
        ? 'Nenhuma outra indicação do mesmo tema no bairro nos 90 dias anteriores.'
        : `${formatarNumero(anteriores)} outra(s) indicação(ões) do mesmo tema no bairro nos 90 dias anteriores.`,
  }
}

function textosDaOuvidoria(item: OcorrenciaClassificada): TextosDaOcorrencia {
  const canal = item.canal ? `canal ${item.canal.toLowerCase()}` : 'canal não informado'
  return {
    titulo: nomeDaCategoria(item.servico),
    contexto: `${nomeDaCategoria(item.natureza)} · ${nomeDaCategoria(item.orgao)} · ${canal}`,
    tempo: `Registrada em ${formatarData(item.dataAbertura)}; prazo legal em ${formatarData(item.dataPrazo)}: ${formatarNumero(item.diasAlemDoPrazo ?? 0)} dias além do prazo.`,
    repeticao: 'Sem lugar na base aberta: risco, vulnerabilidade e reincidência não se aplicam.',
  }
}

export function textosDaOcorrencia(
  item: OcorrenciaClassificada,
  fonte: FonteDaFila,
  nomeDoBairro: string,
): TextosDaOcorrencia {
  if (fonte === '156') return textosDo156(item, nomeDoBairro)
  if (fonte === 'camara') return textosDaCamara(item, nomeDoBairro)
  return textosDaOuvidoria(item)
}
