import type { ButtonHTMLAttributes } from 'react'

import { classesDoBotao, type VarianteDoBotao } from './classesDoBotao'

interface Propriedades extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: VarianteDoBotao
  larguraTotal?: boolean
  compacto?: boolean
}

export function Botao({
  variante = 'primario',
  larguraTotal,
  compacto,
  type = 'button',
  className,
  ...resto
}: Propriedades) {
  const classes = [classesDoBotao(variante, { larguraTotal, compacto }), className]
    .filter(Boolean)
    .join(' ')
  return <button type={type} className={classes} {...resto} />
}
