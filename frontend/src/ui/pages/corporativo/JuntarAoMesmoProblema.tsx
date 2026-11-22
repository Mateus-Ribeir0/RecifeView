import type { MesmoProblemaDoOrgao } from '../../../domain/corporativo'
import { formatarData } from '../../../domain/formatacao'
import estilos from './Corporativo.module.css'

interface Propriedades {
  juntaveis: readonly MesmoProblemaDoOrgao[]
  escolhidas: ReadonlySet<number>
  aoAlternar: (id: number) => void
}

/** As certas já vêm marcadas; as prováveis o órgão confere antes de juntar. */
export function JuntarAoMesmoProblema({ juntaveis, escolhidas, aoAlternar }: Propriedades) {
  if (juntaveis.length === 0) return null
  return (
    <fieldset className={estilos.campo}>
      <legend>Aplicar a mesma resposta ao mesmo problema</legend>
      <div className={estilos.escolhas}>
        {juntaveis.map((parecido) => (
          <label key={parecido.id} className={estilos.escolha}>
            <input
              type="checkbox"
              checked={escolhidas.has(parecido.id)}
              onChange={() => aoAlternar(parecido.id)}
            />
            <span>
              <strong>{parecido.codigo}</strong>
              <small>
                {parecido.certo ? 'Mesma ocorrência' : 'Provável'}, aberta em{' '}
                {formatarData(parecido.dataAbertura)}
              </small>
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  )
}
