const NUMERO = new Intl.NumberFormat('pt-BR')
const HORA = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' })

export function formatarNumero(valor: number): string {
  return NUMERO.format(valor)
}

export function formatarHora(data: Date): string {
  return HORA.format(data)
}
