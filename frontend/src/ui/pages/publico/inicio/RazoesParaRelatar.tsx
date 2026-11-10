import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { RAZOES_PARA_RELATAR } from '../conteudo'
import secao from '../Secao.module.css'
import estilos from './RazoesParaRelatar.module.css'

const PASSO_DO_ATRASO_EM_MS = 80

export function RazoesParaRelatar() {
  return (
    <section className={`${secao.secao} ${secao.fundoClaro}`} aria-labelledby="titulo-razoes">
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>Por que relatar aqui</p>
          <h2 id="titulo-razoes" className={secao.titulo}>
            O que muda para quem relata
          </h2>
        </Aparecer>
        <ul className={estilos.grade}>
          {RAZOES_PARA_RELATAR.map(({ icone, antes, agora }, indice) => (
            <li key={antes}>
              <Aparecer atraso={indice * PASSO_DO_ATRASO_EM_MS} className={estilos.cartao}>
                <span className={estilos.icone}>
                  <Icone nome={icone} tamanho={24} />
                </span>
                <p className={estilos.antes}>
                  <span>Antes</span>
                  {antes}
                </p>
                <p className={estilos.agora}>
                  <span>Agora</span>
                  {agora}
                </p>
              </Aparecer>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
