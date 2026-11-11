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
            Acompanhe o seu pedido até o órgão que resolve
          </h1>
          <p className={estilos.descricao}>
            Você pede no Conecta Recife, na Central 156 ou na Ouvidoria. Aqui você vê em que pé
            está, para qual órgão a gestão encaminhou e o que ele respondeu. E, se viu um problema
            na rua, relata em um minuto, sem dar seus dados.
          </p>
          <div className={estilos.acoes}>
            <LinkDeBotao para="/acompanhar" variante="claro">
              Acompanhar um pedido
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
