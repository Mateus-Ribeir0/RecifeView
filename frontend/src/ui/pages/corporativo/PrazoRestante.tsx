import {
  descreverPrazo,
  estaAberta,
  prazoPedeAtencao,
  type OcorrenciaNaFila,
} from '../../../domain/corporativo'
import { formatarData } from '../../../domain/formatacao'
import estilos from './Corporativo.module.css'

type Prazo = Pick<OcorrenciaNaFila, 'situacao' | 'atrasado' | 'diasParaOPrazo' | 'prazoDeResposta'>

export function PrazoRestante({ item }: { item: Prazo }) {
  if (!estaAberta(item.situacao)) {
    return <span className={estilos.prazo}>Prazo era {formatarData(item.prazoDeResposta)}</span>
  }
  const classe = item.atrasado
    ? estilos.prazoVencido
    : prazoPedeAtencao(item)
      ? estilos.prazoComAlerta
      : ''
  return (
    <span className={`${estilos.prazo} ${classe}`}>
      Prazo {formatarData(item.prazoDeResposta)}, {descreverPrazo(item.diasParaOPrazo)}
    </span>
  )
}
