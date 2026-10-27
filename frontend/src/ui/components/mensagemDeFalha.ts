import { ErroDoRecifeView } from '../../domain/erros'
import { formatarHora } from '../../domain/formatacao'

const MENSAGEM_GENERICA = 'Não foi possível concluir agora. Tente de novo em alguns minutos.'

export function mensagemDeFalha(erro: unknown): string {
  if (!(erro instanceof ErroDoRecifeView)) return MENSAGEM_GENERICA
  if (erro.codigo === 'conta_bloqueada' && erro.desbloqueioEm) {
    return `Muitas tentativas sem sucesso. Por segurança, a conta fica bloqueada até as ${formatarHora(erro.desbloqueioEm)}.`
  }
  return erro.message
}
