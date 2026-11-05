const LOCALIDADE = 'pt-BR'
const HORA = new Intl.DateTimeFormat(LOCALIDADE, { hour: '2-digit', minute: '2-digit' })
const DATA_E_HORA = new Intl.DateTimeFormat(LOCALIDADE, { dateStyle: 'short', timeStyle: 'short' })
const DIAS_DA_SEMANA = [
  'domingo',
  'segunda-feira',
  'terça-feira',
  'quarta-feira',
  'quinta-feira',
  'sexta-feira',
  'sábado',
]
const MESES = [
  'janeiro',
  'fevereiro',
  'março',
  'abril',
  'maio',
  'junho',
  'julho',
  'agosto',
  'setembro',
  'outubro',
  'novembro',
  'dezembro',
]
const BYTES_POR_KB = 1024

export const SEM_DADO = 'sem dado'

export function formatarNumero(valor: number, casas = 0): string {
  return new Intl.NumberFormat(LOCALIDADE, {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  }).format(valor)
}

export function formatarNumeroOpcional(valor: number | null | undefined, casas = 0): string {
  return valor === null || valor === undefined ? SEM_DADO : formatarNumero(valor, casas)
}

export function formatarPorcentagem(valor: number | null | undefined, casas = 0): string {
  return valor === null || valor === undefined ? SEM_DADO : `${formatarNumero(valor, casas)}%`
}

export function formatarDias(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return SEM_DADO
  return Math.round(valor) === 1 ? '1 dia' : `${formatarNumero(valor)} dias`
}

export function formatarHora(data: Date): string {
  return HORA.format(data)
}

export function dataDoIso(iso: string): Date {
  return new Date(`${iso.slice(0, 10)}T12:00:00`)
}

export function isoDaData(data: Date): string {
  const mes = String(data.getMonth() + 1).padStart(2, '0')
  const dia = String(data.getDate()).padStart(2, '0')
  return `${data.getFullYear()}-${mes}-${dia}`
}

export function formatarData(iso: string | null | undefined): string {
  if (!iso) return SEM_DADO
  const [ano, mes, dia] = iso.slice(0, 10).split('-')
  return `${dia}/${mes}/${ano}`
}

export function formatarDiaEMes(iso: string): string {
  const [, mes, dia] = iso.slice(0, 10).split('-')
  return `${dia}/${mes}`
}

export function formatarDataLonga(iso: string): string {
  const data = dataDoIso(iso)
  const diaDaSemana = nomeDoDiaDaSemana(iso)
  const inicio = diaDaSemana.charAt(0).toUpperCase() + diaDaSemana.slice(1)
  return `${inicio}, ${data.getDate()} de ${MESES[data.getMonth()] ?? ''} de ${data.getFullYear()}`
}

export function nomeDoDiaDaSemana(iso: string): string {
  return DIAS_DA_SEMANA[dataDoIso(iso).getDay()] ?? ''
}

export function formatarDataEHora(iso: string | null | undefined): string {
  return iso ? DATA_E_HORA.format(new Date(iso)) : SEM_DADO
}

export function formatarPeriodo(inicio: number, fim: number): string {
  return inicio === fim ? String(inicio) : `${inicio} a ${fim}`
}

export function formatarTamanho(bytes: number): string {
  const megabytes = bytes / BYTES_POR_KB / BYTES_POR_KB
  if (megabytes >= 1) return `${formatarNumero(megabytes, 1)} MB`
  return `${formatarNumero(bytes / BYTES_POR_KB)} KB`
}
