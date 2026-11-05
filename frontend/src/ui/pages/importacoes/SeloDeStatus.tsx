import { ROTULOS_DOS_STATUS, type StatusDaImportacao } from '../../../domain/importacoes'
import estilos from './Importacoes.module.css'

const CLASSES: Partial<Record<StatusDaImportacao, string>> = {
  CONCLUIDA: estilos.seloSucesso,
  FALHOU: estilos.seloErro,
  AGUARDANDO_COLUNAS: estilos.seloAlerta,
  AGUARDANDO_DECISOES: estilos.seloAlerta,
  PRONTA: estilos.seloAlerta,
}

export function SeloDeStatus({ status }: { status: StatusDaImportacao }) {
  return (
    <span className={`${estilos.selo} ${CLASSES[status] ?? ''}`}>{ROTULOS_DOS_STATUS[status]}</span>
  )
}
