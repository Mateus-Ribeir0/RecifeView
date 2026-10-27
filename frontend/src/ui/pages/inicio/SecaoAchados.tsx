import { ACHADOS, NOTA_DOS_ACHADOS } from './conteudo'
import secao from './Secao.module.css'
import estilos from './SecaoAchados.module.css'

export function SecaoAchados() {
  return (
    <section
      id="dados"
      className={`${secao.secao} ${estilos.fundo}`}
      aria-labelledby="titulo-dados"
    >
      <div className="conteudo">
        <p className={`${secao.rotulo} ${secao.rotuloSobreAzulClaro}`}>O que os dados mostram</p>
        <h2 id="titulo-dados" className={secao.titulo}>
          Os primeiros números já mostram onde olhar
        </h2>
        <p className={secao.abertura}>{NOTA_DOS_ACHADOS}</p>
        <ul className={estilos.grade}>
          {ACHADOS.map(({ destaque, afirmacao, contexto, fonte }) => (
            <li key={destaque} className={estilos.cartao}>
              <p className={`numero ${estilos.destaque}`}>{destaque}</p>
              <p className={estilos.afirmacao}>{afirmacao}</p>
              <p className={estilos.contexto}>{contexto}</p>
              <p className={estilos.fonte}>Fonte: {fonte}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
