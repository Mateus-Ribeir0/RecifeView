import { formatarNumero, formatarPorcentagem } from '../../domain/formatacao'
import estilos from './BarraDeComposicao.module.css'

export interface ParteDaComposicao {
  chave: string
  rotulo: string
  valor: number
  cor: string
  detalhe?: string
  textoEscuro?: boolean
}

interface Propriedades {
  partes: readonly ParteDaComposicao[]
  unidade: string
}

const MINIMO_PARA_ROTULO = 7

export function BarraDeComposicao({ partes, unidade }: Propriedades) {
  const total = partes.reduce((soma, parte) => soma + parte.valor, 0)
  const pct = (valor: number) => (total > 0 ? (valor / total) * 100 : 0)
  const descricao = partes
    .map((parte) => `${parte.rotulo}: ${formatarPorcentagem(pct(parte.valor))}`)
    .join(', ')

  return (
    <div>
      <div className={estilos.barra} role="img" aria-label={`${unidade}. ${descricao}`}>
        {partes.map((parte) => (
          <span
            key={parte.chave}
            className={estilos.parte}
            style={{
              flexGrow: parte.valor,
              background: parte.cor,
              color: parte.textoEscuro ? 'var(--cor-preto)' : undefined,
            }}
            title={`${parte.rotulo}: ${formatarNumero(parte.valor)} ${unidade}`}
          >
            {pct(parte.valor) >= MINIMO_PARA_ROTULO && formatarPorcentagem(pct(parte.valor))}
          </span>
        ))}
      </div>
      <ul className={estilos.legenda}>
        {partes.map((parte) => (
          <li key={parte.chave}>
            <span className={estilos.marca} style={{ background: parte.cor }} aria-hidden="true" />
            <span className={estilos.nome}>{parte.rotulo}</span>
            {parte.detalhe && <span className={estilos.detalhe}>{parte.detalhe}</span>}
            <strong className="numero">{formatarNumero(parte.valor)}</strong>
          </li>
        ))}
      </ul>
    </div>
  )
}
