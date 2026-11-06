import estilos from './Botao.module.css'

export type VarianteDoBotao = 'primario' | 'secundario' | 'claro' | 'contorno'

interface OpcoesDoBotao {
  larguraTotal?: boolean
  compacto?: boolean
}

export function classesDoBotao(variante: VarianteDoBotao, opcoes: OpcoesDoBotao = {}): string {
  return [
    estilos.botao,
    estilos[variante],
    opcoes.larguraTotal && estilos.larguraTotal,
    opcoes.compacto && estilos.compacto,
  ]
    .filter(Boolean)
    .join(' ')
}
