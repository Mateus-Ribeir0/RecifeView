import {
  ROTULOS_DAS_SITUACOES,
  ROTULOS_DOS_AUTORES,
  type EventoDoEncaminhamento,
} from '../../../domain/encaminhamentos'
import { formatarDataEHora } from '../../../domain/formatacao'
import estilos from './Encaminhamentos.module.css'

interface Propriedades {
  eventos: readonly EventoDoEncaminhamento[]
  comObservacao?: boolean
}

export function LinhaDoTempo({ eventos, comObservacao = false }: Propriedades) {
  return (
    <ol className={estilos.linhaDoTempo} aria-label="Etapas do encaminhamento">
      {eventos.map((evento, indice) => (
        <li key={`${evento.ocorridoEm}-${indice}`}>
          <time dateTime={evento.ocorridoEm}>{formatarDataEHora(evento.ocorridoEm)}</time>
          <strong>
            {ROTULOS_DAS_SITUACOES[evento.situacao]}, {ROTULOS_DOS_AUTORES[evento.autor]}
          </strong>
          {evento.protocoloDoOrgao && <span>Protocolo no órgão: {evento.protocoloDoOrgao}</span>}
          {comObservacao && evento.observacao && <span>{evento.observacao}</span>}
        </li>
      ))}
    </ol>
  )
}
