import { Aparecer } from '../../../components/Aparecer'
import { ExploradorDoRecife } from '../ExploradorDoRecife'
import secao from '../Secao.module.css'
import estilos from './SecaoDoMapa.module.css'

export function SecaoDoMapa() {
  return (
    <section
      className={`${secao.secao} ${secao.fundoClaro}`}
      aria-labelledby="titulo-mapa-do-recife"
    >
      <div className={`conteudo ${estilos.grade}`}>
        <Aparecer>
          <p className={secao.rotulo}>Território</p>
          <h2 id="titulo-mapa-do-recife" className={secao.titulo}>
            Feito para o Recife, bairro por bairro
          </h2>
          <p className={secao.abertura}>
            Todos os indicadores usam os 94 bairros oficiais e as 6 RPAs. Quando o assunto é
            comparar lugares, o painel usa taxa por mil habitantes, porque mais pedidos num bairro
            não quer dizer mais problema.
          </p>
        </Aparecer>
        <Aparecer atraso={120} className={estilos.mapa}>
          <ExploradorDoRecife />
        </Aparecer>
      </div>
    </section>
  )
}
