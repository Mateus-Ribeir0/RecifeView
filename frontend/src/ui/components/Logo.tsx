import logoBranco from '../assets/marca/logo-recifeview-branco.png'
import logoColorido from '../assets/marca/logo-recifeview.png'

const PROPORCAO = { colorido: 424 / 96, branco: 412 / 96 } as const

interface Propriedades {
  variante?: keyof typeof PROPORCAO
  altura?: number
}

export function Logo({ variante = 'colorido', altura = 32 }: Propriedades) {
  return (
    <img
      src={variante === 'branco' ? logoBranco : logoColorido}
      alt="RecifeView"
      height={altura}
      width={Math.round(altura * PROPORCAO[variante])}
    />
  )
}
