import { useId, type InputHTMLAttributes, type Ref } from 'react'

import estilos from './Campo.module.css'

export interface PropriedadesDeCampo extends InputHTMLAttributes<HTMLInputElement> {
  rotulo: string
  erro?: string | null
  dica?: string
  ref?: Ref<HTMLInputElement>
}

export function CampoDeTexto({ rotulo, erro, dica, className, ...entrada }: PropriedadesDeCampo) {
  const id = useId()
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
      <input
        id={id}
        className={[estilos.entrada, className].filter(Boolean).join(' ')}
        aria-invalid={erro ? true : undefined}
        aria-describedby={descricoes}
        {...entrada}
      />
      {erro && (
        <p id={idDoErro} className={estilos.erro}>
          {erro}
        </p>
      )}
    </div>
  )
}
