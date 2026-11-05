import estilos from './Medidor.module.css'

interface Propriedades {
  porcentagem: number
  rotulo: string
}

const LIMITE = 100

export function Medidor({ porcentagem, rotulo }: Propriedades) {
  const largura = Math.min(Math.max(porcentagem, 0), LIMITE)
  return (
    <div className={estilos.trilho} role="img" aria-label={rotulo}>
      <span className={estilos.parte} style={{ width: `${largura}%` }} />
    </div>
  )
}
