import { TELAS_DO_PAINEL } from '../../conteudo/telasDoPainel'
import { PERGUNTAS_DA_GESTAO } from './conteudo'
import secao from './Secao.module.css'
import estilos from './SecaoPainel.module.css'

export function SecaoPainel() {
  return (
    <section id="painel" className={secao.secao} aria-labelledby="titulo-painel">
      <div className={`conteudo ${estilos.grade}`}>
        <div>
          <p className={secao.rotulo}>O painel</p>
          <h2 id="titulo-painel" className={secao.titulo}>
            Um painel para fazer perguntas melhores
          </h2>
          <p className={secao.abertura}>
            Ao escolher um serviço, um período e uma região, o gestor vê onde as solicitações se
            concentram, quais locais voltam a aparecer e quanto tempo o atendimento leva.
          </p>
          <ul className={estilos.perguntas} aria-label="Perguntas que o painel ajuda a responder">
            {PERGUNTAS_DA_GESTAO.map((pergunta) => (
              <li key={pergunta}>{pergunta}</li>
            ))}
          </ul>
          <p className={estilos.limite}>
            O painel organiza as evidências. A decisão continua com a gestão e com os critérios da
            Prefeitura.
          </p>
        </div>
        <div>
          <div className={estilos.cabecalhoDasTelas}>
            <h3>O que vem no painel</h3>
            <span className={estilos.situacao}>Em desenvolvimento</span>
          </div>
          <ul className={estilos.telas}>
            {TELAS_DO_PAINEL.map(({ nome, mostra }) => (
              <li key={nome}>
                <h4>{nome}</h4>
                <p>{mostra}</p>
              </li>
            ))}
          </ul>
          <p className={`${secao.nota} ${estilos.nota}`}>
            As telas entram ao longo de novembro e dezembro de 2026.
          </p>
        </div>
      </div>
    </section>
  )
}
