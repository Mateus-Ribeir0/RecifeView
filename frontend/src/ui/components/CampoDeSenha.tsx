import { useId, useState } from 'react'

import estilos from './Campo.module.css'
import type { PropriedadesDeCampo } from './CampoDeTexto'

export function CampoDeSenha({ rotulo, erro, dica, ...entrada }: PropriedadesDeCampo) {
  const id = useId()
  const [visivel, definirVisivel] = useState(false)
  const idDaDica = dica ? `${id}-dica` : undefined
  const idDoErro = erro ? `${id}-erro` : undefined
  const descricoes = [idDaDica, idDoErro].filter(Boolean).join(' ') || undefined

  return (
    <div className={estilos.campo}>
      <label htmlFor={id} className={estilos.rotulo}>
        {rotulo}
      </label>
      {dica && (
        <p id={idDaDica} className={estilos.dica}>
          {dica}
        </p>
      )}
      <div className={estilos.caixa}>
        <input
          id={id}
          type={visivel ? 'text' : 'password'}
          className={`${estilos.entrada} ${estilos.comAlternador}`}
          aria-invalid={erro ? true : undefined}
          aria-describedby={descricoes}
          {...entrada}
        />
        <button
          type="button"
          className={estilos.alternador}
          aria-controls={id}
          aria-label={
            visivel ? `Ocultar ${rotulo.toLowerCase()}` : `Mostrar ${rotulo.toLowerCase()}`
          }
          onClick={() => definirVisivel((atual) => !atual)}
        >
          {visivel ? 'Ocultar' : 'Mostrar'}
        </button>
      </div>
      {erro && (
        <p id={idDoErro} className={estilos.erro}>
          {erro}
        </p>
      )}
    </div>
  )
}
