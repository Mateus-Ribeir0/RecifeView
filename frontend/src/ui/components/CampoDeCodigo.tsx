import { mascararCodigo } from '../../domain/conta'
import estilos from './CampoDeCodigo.module.css'
import { CampoDeTexto } from './CampoDeTexto'

interface Propriedades {
  valor: string
  aoMudar: (valor: string) => void
  erro?: string | null
}

export function CampoDeCodigo({ valor, aoMudar, erro }: Propriedades) {
  return (
    <CampoDeTexto
      rotulo="Código de 6 dígitos"
      dica="Ele chegou no seu e-mail e vale por 15 minutos."
      className={estilos.codigo}
      inputMode="numeric"
      autoComplete="one-time-code"
      placeholder="000 000"
      maxLength={7}
      value={valor}
      erro={erro}
      onChange={(evento) => aoMudar(mascararCodigo(evento.target.value))}
    />
  )
}
