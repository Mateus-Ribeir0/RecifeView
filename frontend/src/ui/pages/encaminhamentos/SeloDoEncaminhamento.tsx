import {
  ROTULOS_DAS_SITUACOES,
  type SituacaoDoEncaminhamento,
} from '../../../domain/encaminhamentos'
import estilos from './Encaminhamentos.module.css'

const CLASSES: Readonly<Record<SituacaoDoEncaminhamento, string | undefined>> = {
  enviado: estilos.seloAguardando,
  falhou: estilos.seloFalha,
  recebido: estilos.seloRecebido,
  resolvido: estilos.seloResolvido,
  devolvido: undefined,
}

interface Propriedades {
  situacao: SituacaoDoEncaminhamento
  atrasado?: boolean
}

export function SeloDoEncaminhamento({ situacao, atrasado = false }: Propriedades) {
  return (
    <span className={`${estilos.selo} ${CLASSES[situacao] ?? ''}`}>
      {ROTULOS_DAS_SITUACOES[situacao]}
      {atrasado && <strong className={estilos.atraso}>, prazo vencido</strong>}
    </span>
  )
}
