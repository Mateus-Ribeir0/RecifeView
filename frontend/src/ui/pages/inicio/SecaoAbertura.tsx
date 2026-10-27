import { LinkDeBotao } from '../../components/LinkDeBotao'
import { ExploradorDoRecife } from './ExploradorDoRecife'
import estilos from './SecaoAbertura.module.css'

export function SecaoAbertura() {
  return (
    <section className={estilos.abertura} aria-labelledby="titulo-abertura">
      <div className={`conteudo ${estilos.grade}`}>
        <div>
          <p className={estilos.chamada}>Painel analítico para a gestão pública do Recife</p>
          <h1 id="titulo-abertura" className={estilos.titulo}>
            Onde as demandas do Recife se repetem, demoram ou ficam sem resposta
          </h1>
          <p className={estilos.descricao}>
            O RecifeView reúne os registros da Central 156, da Ouvidoria, da Defesa Civil, da SEDEC
            e da Câmara Municipal num só painel, organizado por bairro, serviço e período.
          </p>
          <div className={estilos.acoes}>
            <LinkDeBotao para="/entrar">Entrar no painel</LinkDeBotao>
            <LinkDeBotao para="#dados" variante="secundario">
              Ver o que os dados mostram
            </LinkDeBotao>
          </div>
          <p className={estilos.restricao}>Acesso restrito a gestores públicos cadastrados.</p>
        </div>
        <ExploradorDoRecife />
      </div>
    </section>
  )
}
