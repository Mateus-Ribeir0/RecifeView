import { formatarPorcentagem } from '../../domain/formatacao'
import type { ParteDaComposicao } from './BarraDeComposicao'
import estilos from './ComposicaoPorLinha.module.css'

export interface LinhaDaComposicao {
  chave: string
  rotulo: string
  partes: readonly ParteDaComposicao[]
}

interface Propriedades {
  linhas: readonly LinhaDaComposicao[]
  selecionada?: string | null
  aoSelecionar?: (chave: string | null) => void
}

function descrever({ rotulo, partes }: LinhaDaComposicao): string {
  const total = partes.reduce((soma, parte) => soma + parte.valor, 0) || 1
  const fatias = partes.map(
    (parte) => `${parte.rotulo}: ${formatarPorcentagem((parte.valor / total) * 100)}`,
  )
  return `${rotulo}. ${fatias.join(', ')}`
}

export function ComposicaoPorLinha({ linhas, selecionada, aoSelecionar }: Propriedades) {
  return (
    <ul className={estilos.linhas}>
      {linhas.map((linha) => (
        <li key={linha.chave}>
          <button
            type="button"
            className={estilos.linha}
            aria-label={descrever(linha)}
            aria-pressed={selecionada === linha.chave}
            data-apagada={(selecionada && selecionada !== linha.chave) || undefined}
            onClick={() => aoSelecionar?.(selecionada === linha.chave ? null : linha.chave)}
          >
            <span className={estilos.rotulo}>{linha.rotulo}</span>
            <span className={estilos.barra}>
              {linha.partes.map((parte) => (
                <span
                  key={parte.chave}
                  style={{ flexGrow: parte.valor, background: parte.cor }}
                  title={parte.rotulo}
                />
              ))}
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
