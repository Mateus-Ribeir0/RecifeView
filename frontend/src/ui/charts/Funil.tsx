import { formatarNumero, formatarPorcentagem } from '../../domain/formatacao'
import estilos from './Funil.module.css'

export interface EtapaDoFunil {
  chave: string
  rotulo: string
  valor: number
}

function fracao(parte: number, todo: number): number {
  return todo > 0 ? (parte / todo) * 100 : 0
}

export function Funil({ etapas }: { etapas: readonly EtapaDoFunil[] }) {
  const inicio = etapas[0]?.valor ?? 0
  return (
    <ol className={estilos.funil}>
      {etapas.map((etapa, indice) => {
        const anterior = etapas[indice - 1]
        const perda = anterior ? fracao(anterior.valor - etapa.valor, anterior.valor) : 0
        return (
          <li key={etapa.chave} className={estilos.etapa}>
            {anterior && (
              <p className={estilos.perda}>
                {formatarNumero(anterior.valor - etapa.valor)} ficam pelo caminho (
                {formatarPorcentagem(perda)})
              </p>
            )}
            <div className={estilos.linha}>
              <span className={estilos.rotulo}>{etapa.rotulo}</span>
              <span className={`${estilos.numero} numero`}>
                {formatarNumero(etapa.valor)}{' '}
                <span className={estilos.parte}>
                  {formatarPorcentagem(fracao(etapa.valor, inicio))}
                </span>
              </span>
            </div>
            <div className={estilos.trilho} aria-hidden="true">
              <span
                className={estilos.barra}
                data-etapa={indice}
                style={{ width: `${fracao(etapa.valor, inicio)}%` }}
              />
            </div>
          </li>
        )
      })}
    </ol>
  )
}
