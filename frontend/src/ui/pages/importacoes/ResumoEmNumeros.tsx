import { formatarNumero } from '../../../domain/formatacao'
import { ROTULOS_DAS_CORRECOES, ROTULOS_DOS_DESCARTES } from '../../../domain/importacoes'
import { KpiCard } from '../../components/KpiCard'
import estilos from './Importacoes.module.css'

interface NumeroDoResumo {
  rotulo: string
  valor: number
  contexto?: string
}

interface Propriedades {
  numeros: readonly NumeroDoResumo[]
  descartes: Readonly<Record<string, number>>
  correcoes: Readonly<Record<string, number>>
}

export function ResumoEmNumeros({ numeros, descartes, correcoes }: Propriedades) {
  const listaDeDescartes = Object.entries(descartes)
  const listaDeCorrecoes = Object.entries(correcoes)
  return (
    <>
      <div className={estilos.numeros}>
        {numeros.map((numero) => (
          <KpiCard
            key={numero.rotulo}
            rotulo={numero.rotulo}
            valor={formatarNumero(numero.valor)}
            contexto={numero.contexto}
          />
        ))}
      </div>
      <div className={estilos.listasDoResumo}>
        <div>
          <h3>Linhas descartadas</h3>
          {listaDeDescartes.length === 0 ? (
            <p>Nenhuma.</p>
          ) : (
            <ul>
              {listaDeDescartes.map(([motivo, n]) => (
                <li key={motivo}>
                  {ROTULOS_DOS_DESCARTES[motivo] ?? motivo}: {formatarNumero(n)}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h3>Correções aplicadas</h3>
          {listaDeCorrecoes.length === 0 ? (
            <p>Nenhuma.</p>
          ) : (
            <ul>
              {listaDeCorrecoes.map(([correcao, n]) => (
                <li key={correcao}>
                  {ROTULOS_DAS_CORRECOES[correcao] ?? correcao}: {formatarNumero(n)}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  )
}
