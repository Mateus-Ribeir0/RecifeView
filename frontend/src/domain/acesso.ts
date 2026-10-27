// Espelham as regras de backend/app/domain/usuario.py: mudar lá exige mudar aqui.
export const TENTATIVAS_ANTES_DO_BLOQUEIO = 5
export const MINUTOS_DE_BLOQUEIO = 15

const FORMATO_DE_EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

export function pareceEmail(texto: string): boolean {
  return FORMATO_DE_EMAIL.test(texto.trim())
}
