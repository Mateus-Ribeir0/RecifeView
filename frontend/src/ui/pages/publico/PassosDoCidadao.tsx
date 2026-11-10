import { Aparecer } from '../../components/Aparecer'
import { Icone } from '../../components/Icone'
import { PASSOS_DO_CIDADAO } from './conteudo'
import estilos from './PassosDoCidadao.module.css'

const PASSO_DO_ATRASO_EM_MS = 110

export function PassosDoCidadao() {
  return (
    <ol className={estilos.passos}>
      {PASSOS_DO_CIDADAO.map(({ icone, titulo, texto }, indice) => (
        <li key={titulo}>
          <Aparecer atraso={indice * PASSO_DO_ATRASO_EM_MS} className={estilos.passo}>
            <span className={estilos.numero} aria-hidden="true">
              {indice + 1}
            </span>
            <span className={estilos.icone}>
              <Icone nome={icone} tamanho={26} />
            </span>
            <h3>{titulo}</h3>
            <p>{texto}</p>
          </Aparecer>
        </li>
      ))}
    </ol>
  )
}
