import capturaDaCidade from '../../../assets/capturas/cidade.webp'
import fotoDoRecife from '../../../assets/imagens/recife-skyline.jpg'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import estilos from './Abertura.module.css'

export function Abertura() {
  return (
    <section className={estilos.abertura} aria-labelledby="titulo-abertura">
      <div className={estilos.faixa}>
        <img src={fotoDoRecife} alt="" className={estilos.foto} />
        <div className={`conteudo ${estilos.texto}`}>
          <p className={estilos.chamada}>Para quem mora no Recife</p>
          <h1 id="titulo-abertura" className={estilos.titulo}>
            Relate um problema na sua rua e acompanhe o que já foi relatado no seu bairro
          </h1>
          <p className={estilos.descricao}>
            Buraco, lâmpada apagada, entulho, galeria entupida. O relato leva um minuto e não pede
            seus dados. Com uma conta, você vê o que outras pessoas relataram e em que pé está cada
            caso.
          </p>
          <div className={estilos.acoes}>
            <LinkDeBotao para="/cadastrar" variante="claro">
              Criar conta
            </LinkDeBotao>
            <LinkDeBotao para="/contribuir" variante="contorno">
              Relatar sem conta
            </LinkDeBotao>
          </div>
        </div>
      </div>
      <div className={`conteudo ${estilos.vitrine}`}>
        <figure className={estilos.moldura}>
          <img
            src={capturaDaCidade}
            width={1440}
            height={900}
            alt="Área do cidadão no RecifeView: mapa dos bairros com relato e a lista de relatos com a situação de cada um"
          />
        </figure>
        <p className={estilos.legenda}>
          Área do cidadão com relatos de demonstração (dado fictício).
        </p>
      </div>
    </section>
  )
}
