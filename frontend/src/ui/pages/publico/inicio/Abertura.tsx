import capturaDoInicio from '../../../assets/capturas/inicio.webp'
import fotoDoRecife from '../../../assets/imagens/recife-skyline.jpg'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import estilos from './Abertura.module.css'

export function Abertura() {
  return (
    <section className={estilos.abertura} aria-labelledby="titulo-abertura">
      <div className={estilos.faixa}>
        <img src={fotoDoRecife} alt="" className={estilos.foto} />
        <div className={`conteudo ${estilos.texto}`}>
          <p className={estilos.chamada}>Plataforma de análise das demandas urbanas do Recife</p>
          <h1 id="titulo-abertura" className={estilos.titulo}>
            Onde as demandas do Recife se repetem, demoram ou ficam sem resposta
          </h1>
          <p className={estilos.descricao}>
            A Central 156, a Ouvidoria, a Defesa Civil, a SEDEC e a Câmara Municipal numa leitura
            só, por bairro, serviço e período, para a gestão decidir com o quadro inteiro na frente.
          </p>
          <div className={estilos.acoes}>
            <LinkDeBotao para="/entrar" variante="claro">
              Entrar no painel
            </LinkDeBotao>
            <LinkDeBotao para="/o-que-muda" variante="contorno">
              Ver o que muda
            </LinkDeBotao>
          </div>
        </div>
      </div>
      <div className={`conteudo ${estilos.vitrine}`}>
        <figure className={estilos.moldura}>
          <img
            src={capturaDoInicio}
            width={1440}
            height={900}
            alt="Tela inicial do painel do RecifeView, com indicadores, volume por fonte e mapa dos bairros"
          />
        </figure>
        <p className={estilos.legenda}>Tela real do painel, com a base de 07/10/2026.</p>
      </div>
    </section>
  )
}
