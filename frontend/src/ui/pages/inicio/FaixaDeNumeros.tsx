import { NOTA_DO_DATASET, NUMEROS_DO_DATASET } from './conteudo'
import estilos from './FaixaDeNumeros.module.css'
import secao from './Secao.module.css'

export function FaixaDeNumeros() {
  return (
    <section className={estilos.faixa} aria-label="A base do RecifeView em números">
      <div className="conteudo">
        <dl className={estilos.numeros}>
          {NUMEROS_DO_DATASET.map(({ valor, rotulo }) => (
            <div key={rotulo} className={estilos.item}>
              <dt className={estilos.rotulo}>{rotulo}</dt>
              <dd className={`numero ${estilos.valor}`}>{valor}</dd>
            </div>
          ))}
        </dl>
        <p className={`${secao.nota} ${estilos.nota}`}>Fonte: {NOTA_DO_DATASET}</p>
      </div>
    </section>
  )
}
