import estilos from './Legenda.module.css'

export interface ItemDaLegenda {
  chave: string
  rotulo: string
  cor: string
}

interface Propriedades {
  itens: readonly ItemDaLegenda[]
  foco?: string | null
  aoEscolher?: (chave: string | null) => void
}

export function Legenda({ itens, foco, aoEscolher }: Propriedades) {
  return (
    <ul className={estilos.legenda}>
      {itens.map((item) => {
        const apagado = Boolean(foco) && foco !== item.chave
        const marca = (
          <span className={estilos.marca} style={{ background: item.cor }} aria-hidden="true" />
        )
        return (
          <li key={item.chave} className={apagado ? estilos.apagado : undefined}>
            {aoEscolher ? (
              <button
                type="button"
                className={estilos.botao}
                aria-pressed={foco === item.chave}
                onClick={() => aoEscolher(foco === item.chave ? null : item.chave)}
              >
                {marca}
                {item.rotulo}
              </button>
            ) : (
              <span className={estilos.item}>
                {marca}
                {item.rotulo}
              </span>
            )}
          </li>
        )
      })}
    </ul>
  )
}
