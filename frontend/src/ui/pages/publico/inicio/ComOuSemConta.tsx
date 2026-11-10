import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import { PassosDoCidadao } from '../PassosDoCidadao'
import secao from '../Secao.module.css'
import estilos from './ComOuSemConta.module.css'

const SEM_CONTA = [
  'Relatar um problema em um minuto',
  'Ver os números da cidade nos dados abertos',
] as const

const COM_CONTA = [
  'Ver os relatos da cidade e da sua rua',
  'Acompanhar a situação de cada relato',
  'Comparar o seu bairro com o Recife',
] as const

export function ComOuSemConta() {
  return (
    <section className={secao.secao} aria-labelledby="titulo-como-funciona">
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>Como funciona</p>
          <h2 id="titulo-como-funciona" className={secao.titulo}>
            Do seu relato até a gestão, e de volta para você
          </h2>
        </Aparecer>
        <PassosDoCidadao />
        <div className={estilos.planos}>
          <Aparecer className={estilos.plano}>
            <h3>Sem conta</h3>
            <ul>
              {SEM_CONTA.map((item) => (
                <li key={item}>
                  <Icone nome="confirmado" tamanho={20} />
                  {item}
                </li>
              ))}
            </ul>
            <LinkDeBotao para="/contribuir" variante="secundario">
              Relatar sem conta
            </LinkDeBotao>
          </Aparecer>
          <Aparecer atraso={120} className={`${estilos.plano} ${estilos.planoEmDestaque}`}>
            <h3>Com conta gratuita</h3>
            <ul>
              {[...SEM_CONTA, ...COM_CONTA].map((item) => (
                <li key={item}>
                  <Icone nome="confirmado" tamanho={20} />
                  {item}
                </li>
              ))}
            </ul>
            <LinkDeBotao para="/cadastrar" variante="claro">
              Criar conta
            </LinkDeBotao>
          </Aparecer>
        </div>
      </div>
    </section>
  )
}
