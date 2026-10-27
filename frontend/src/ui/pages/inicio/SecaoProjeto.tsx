import { EQUIPE, LINKS_DO_PROJETO } from './conteudo'
import secao from './Secao.module.css'
import estilos from './SecaoProjeto.module.css'

export function SecaoProjeto() {
  return (
    <section id="projeto" className={secao.secao} aria-labelledby="titulo-projeto">
      <div className={`conteudo ${estilos.grade}`}>
        <div>
          <p className={secao.rotulo}>O projeto</p>
          <h2 id="titulo-projeto" className={secao.titulo}>
            Quem faz o RecifeView
          </h2>
          <p className={secao.abertura}>
            O RecifeView é o projeto do Grupo 08 de Projetos 5 da CESAR School (2026.2), na trilha
            de Análise e Visualização de Dados. Ele responde ao desafio “Fragmentação do Tratamento
            de Denúncias Recebidas via Conecta Recife”, do Banco de Oportunidades da Prefeitura do
            Recife.
          </p>
          <ul className={estilos.links}>
            <li>
              <a href={LINKS_DO_PROJETO.desafio}>Conhecer o desafio</a>
            </li>
            <li>
              <a href={LINKS_DO_PROJETO.site}>Site do projeto</a>
            </li>
            <li>
              <a href={LINKS_DO_PROJETO.codigo}>Código no GitHub</a>
            </li>
          </ul>
          <p className={estilos.aviso}>
            Projeto acadêmico, sem vínculo oficial com a Prefeitura do Recife.
          </p>
        </div>
        <div className={estilos.equipe}>
          <h3>Equipe</h3>
          <ul>
            {EQUIPE.map((integrante) => (
              <li key={integrante}>{integrante}</li>
            ))}
          </ul>
          <h3>Orientação</h3>
          <p>Prof. Marcelo Arcoverde</p>
          <h3>Trilha de Análise e Visualização de Dados</h3>
          <p>Profª Maíra Farias</p>
        </div>
      </div>
    </section>
  )
}
