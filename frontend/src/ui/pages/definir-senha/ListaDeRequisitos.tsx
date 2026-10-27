import type { RequisitoDaSenha } from '../../../domain/senha'
import estilos from './ListaDeRequisitos.module.css'

interface Propriedades {
  id: string
  requisitos: readonly RequisitoDaSenha[]
  destacarPendencias: boolean
}

function Marcador({ atendido }: { atendido: boolean }) {
  return (
    <svg className={estilos.marcador} viewBox="0 0 16 16" aria-hidden="true">
      <circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" strokeWidth="1.5" />
      {atendido && (
        <path
          d="M4.5 8.2l2.2 2.2 4.8-4.8"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}
    </svg>
  )
}

export function ListaDeRequisitos({ id, requisitos, destacarPendencias }: Propriedades) {
  return (
    <ul id={id} className={estilos.lista} aria-label="Requisitos da nova senha">
      {requisitos.map(({ descricao, atendido }) => {
        const situacao = atendido ? estilos.atendido : destacarPendencias && estilos.faltando
        return (
          <li key={descricao} className={[estilos.requisito, situacao].filter(Boolean).join(' ')}>
            <Marcador atendido={atendido} />
            {descricao}
            <span className="visualmente-oculto">{atendido ? ', atendido' : ', pendente'}</span>
          </li>
        )
      })}
    </ul>
  )
}
