import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import { PROBLEMAS, RESUMO_DO_QUE_MUDA } from '../conteudo'
import secao from '../Secao.module.css'
import estilos from './ResumoDoQueMuda.module.css'

const PASSO_DO_ATRASO_EM_MS = 80
const PROBLEMAS_DO_RESUMO = PROBLEMAS.filter(({ chave }) => RESUMO_DO_QUE_MUDA.includes(chave))

export function ResumoDoQueMuda() {
  return (
    <section
      className={`${secao.secao} ${secao.fundoClaro}`}
      aria-labelledby="titulo-resumo-do-que-muda"
    >
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>O que muda</p>
          <h2 id="titulo-resumo-do-que-muda" className={secao.titulo}>
            O cidadão já tinha canais. Faltava enxergar o que acontecia depois deles
          </h2>
        </Aparecer>
        <ul className={estilos.grade}>
          {PROBLEMAS_DO_RESUMO.map(({ chave, icone, titulo, agora }, indice) => (
            <li key={chave}>
              <Aparecer atraso={indice * PASSO_DO_ATRASO_EM_MS} className={estilos.altura}>
                <article className={estilos.cartao}>
                  <span className={estilos.icone}>
                    <Icone nome={icone} tamanho={24} />
                  </span>
                  <h3>{titulo}</h3>
                  <p>{agora}</p>
                </article>
              </Aparecer>
            </li>
          ))}
        </ul>
        <Aparecer className={estilos.acao}>
          <LinkDeBotao para="/o-que-muda">Ver os sete problemas</LinkDeBotao>
        </Aparecer>
      </div>
    </section>
  )
}
