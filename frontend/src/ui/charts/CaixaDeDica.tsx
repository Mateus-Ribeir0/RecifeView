import estilos from './CaixaDeDica.module.css'

export interface LinhaDaDica {
  rotulo: string
  valor: string
  cor?: string
}

interface Propriedades {
  titulo?: string
  linhas: readonly LinhaDaDica[]
}

export function CaixaDeDica({ titulo, linhas }: Propriedades) {
  return (
    <div className={estilos.caixa}>
      {titulo && <p className={estilos.titulo}>{titulo}</p>}
      <ul>
        {linhas.map((linha) => (
          <li key={linha.rotulo} className={estilos.linha}>
            {linha.cor && (
              <span
                className={estilos.marca}
                style={{ background: linha.cor }}
                aria-hidden="true"
              />
            )}
            <strong className="numero">{linha.valor}</strong>
            <span>{linha.rotulo}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
