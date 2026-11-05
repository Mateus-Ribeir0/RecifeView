import estilos from './BarraNaCelula.module.css'

interface Propriedades {
  valor: number
  maximo: number
  texto: string
}

export function BarraNaCelula({ valor, maximo, texto }: Propriedades) {
  const largura = maximo > 0 ? (valor / maximo) * 100 : 0
  return (
    <span className={estilos.celula}>
      <span className={estilos.trilho} aria-hidden="true">
        <span className={estilos.parte} style={{ width: `${largura}%` }} />
      </span>
      <span className={estilos.texto}>{texto}</span>
    </span>
  )
}
