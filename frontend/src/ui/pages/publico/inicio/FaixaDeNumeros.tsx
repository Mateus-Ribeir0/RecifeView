import { Aparecer } from '../../../components/Aparecer'
import { ContadorAnimado } from '../../../components/ContadorAnimado'
import { NOTA_DA_BASE, NUMEROS_DA_BASE } from '../conteudo'
import secao from '../Secao.module.css'
import estilos from './FaixaDeNumeros.module.css'

const PASSO_DO_ATRASO_EM_MS = 90

export function FaixaDeNumeros() {
  return (
    <section className={estilos.faixa} aria-label="A base do RecifeView em números">
      <div className="conteudo">
        <dl className={estilos.numeros}>
          {NUMEROS_DA_BASE.map(({ valor, rotulo }, indice) => (
            <Aparecer key={rotulo} atraso={indice * PASSO_DO_ATRASO_EM_MS}>
              <div className={estilos.item}>
                <dt className={estilos.rotulo}>{rotulo}</dt>
                <dd className={estilos.valor}>
                  <ContadorAnimado valor={valor} />
                </dd>
              </div>
            </Aparecer>
          ))}
        </dl>
        <p className={secao.nota}>{NOTA_DA_BASE}</p>
      </div>
    </section>
  )
}
