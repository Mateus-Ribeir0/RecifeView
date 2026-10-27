import { PORTAS } from './conteudo'
import secao from './Secao.module.css'
import estilos from './SecaoProblema.module.css'

export function SecaoProblema() {
  return (
    <section id="problema" className={secao.secao} aria-labelledby="titulo-problema">
      <div className="conteudo">
        <p className={secao.rotulo}>O problema</p>
        <h2 id="titulo-problema" className={secao.titulo}>
          Por trás de cada registro, existe uma rotina
        </h2>
        <div className={estilos.colunas}>
          <article className={estilos.coluna}>
            <h3 className={estilos.subtitulo}>Na rua</h3>
            <p className={estilos.relato}>
              Rosângela mora no Recife. Há semanas, um buraco na rua dela faz parte da rotina:
              quando chove, ele some debaixo da água, e quem não conhece a rua descobre quando passa
              por cima.
            </p>
            <p className={estilos.relato}>
              Ela registrou o problema, recebeu um protocolo e esperou. Como nada mudou, registrou
              de novo. O vizinho também. Hoje existem vários chamados sobre a mesma rua, e ela
              continua desviando do mesmo buraco.
            </p>
            <p className={estilos.ficcao}>
              Rosângela é uma personagem fictícia, criada pelo grupo para apresentar o problema.
            </p>
          </article>
          <div className={estilos.coluna}>
            <h3 className={estilos.subtitulo}>Na gestão</h3>
            <p className={estilos.relato}>
              Do outro lado, as solicitações chegam por portas diferentes, e cada uma guarda a sua
              própria base:
            </p>
            <ul className={estilos.portas}>
              {PORTAS.map(({ nome, registra }) => (
                <li key={nome}>
                  <strong>{nome}</strong>
                  <span>{registra}</span>
                </li>
              ))}
            </ul>
            <p className={estilos.lacuna}>
              Essas bases não têm um identificador em comum. Vista sozinha, uma repetição parece só
              mais uma solicitação. Vista em conjunto, pode revelar um padrão que merece
              investigação.
            </p>
          </div>
        </div>
        <blockquote className={estilos.citacao}>
          <p>
            Rosângela enxerga um problema. O RecifeView quer ajudar a gestão a enxergar os padrões
            que esse problema revela.
          </p>
        </blockquote>
      </div>
    </section>
  )
}
