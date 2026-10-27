import { LinkDeBotao } from '../../components/LinkDeBotao'
import estilos from './ChamadaDeAcesso.module.css'

export function ChamadaDeAcesso() {
  return (
    <section className={estilos.chamada} aria-labelledby="titulo-acesso">
      <div className={`conteudo ${estilos.grade}`}>
        <div>
          <h2 id="titulo-acesso" className={estilos.titulo}>
            Acesso para gestores públicos
          </h2>
          <p className={estilos.texto}>
            Entre com o e-mail e a senha recebidos da administração do RecifeView. No primeiro
            acesso, você define a sua própria senha.
          </p>
        </div>
        <LinkDeBotao para="/entrar" variante="claro">
          Entrar no painel
        </LinkDeBotao>
      </div>
    </section>
  )
}
