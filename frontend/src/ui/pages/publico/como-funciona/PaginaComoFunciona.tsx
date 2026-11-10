import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import {
  CAMADAS_DO_PENTE_FINO,
  GARANTIAS_DE_PRIVACIDADE,
  LEITURAS_HONESTAS,
  NIVEIS_DE_ACESSO,
} from '../conteudo'
import { PassosDoCidadao } from '../PassosDoCidadao'
import secao from '../Secao.module.css'
import estilos from './PaginaComoFunciona.module.css'

const DESTINOS = [
  {
    titulo: 'Igual',
    regra: 'Mesmo endereço com número, mesmo serviço, até 7 dias.',
    resultado: 'Soma sozinho. Vira uma ocorrência com mais de um relato.',
  },
  {
    titulo: 'Parecido',
    regra: 'Rua, número ou serviço próximos, menos de 30 dias.',
    resultado: 'Uma pessoa da gestão confere os dois lado a lado.',
  },
  {
    titulo: 'Diferente',
    regra: 'Outro lugar, outro tema ou 30 dias ou mais depois.',
    resultado: 'Fica como ocorrência própria. Se voltou, é reincidência.',
  },
] as const

function Marca({ tem, rotulo }: { tem: boolean; rotulo: string }) {
  return (
    <span className={estilos.marcaDeAcesso} data-tem={tem || undefined}>
      <Icone nome={tem ? 'confirmado' : 'fechar'} tamanho={18} />
      <span className="visualmente-oculto">
        {tem ? 'Sim' : 'Não'}, {rotulo}
      </span>
    </span>
  )
}

function TabelaDeAcesso() {
  return (
    <div className={estilos.rolagem}>
      <table className={estilos.tabela}>
        <caption className="visualmente-oculto">O que cada tipo de acesso permite ver</caption>
        <thead>
          <tr>
            <th scope="col">O que dá para ver e fazer</th>
            <th scope="col">Sem conta</th>
            <th scope="col">Cidadão</th>
            <th scope="col">Gestão</th>
          </tr>
        </thead>
        <tbody>
          {NIVEIS_DE_ACESSO.map(({ recurso, semConta, cidadao, gestao }) => (
            <tr key={recurso}>
              <th scope="row">{recurso}</th>
              <td>
                <Marca tem={semConta} rotulo="sem conta" />
              </td>
              <td>
                <Marca tem={cidadao} rotulo="conta de cidadão" />
              </td>
              <td>
                <Marca tem={gestao} rotulo="gestão" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function SecaoDoPenteFino() {
  return (
    <section className={`${secao.secao} ${secao.fundoClaro}`} aria-labelledby="titulo-pente-fino">
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>Pente fino</p>
          <h2 id="titulo-pente-fino" className={secao.titulo}>
            O mesmo problema não vira dez casos
          </h2>
          <p className={secao.abertura}>
            Cada relato é comparado com os outros e com os pedidos oficiais. O que é igual se soma;
            o que é só parecido vai para uma pessoa decidir.
          </p>
        </Aparecer>
        <ol className={estilos.camadas}>
          {CAMADAS_DO_PENTE_FINO.map(({ icone, titulo, texto }, indice) => (
            <li key={titulo}>
              <Aparecer atraso={indice * 70} className={estilos.camada}>
                <span className={estilos.iconeDaCamada}>
                  <Icone nome={icone} tamanho={22} />
                </span>
                <div>
                  <h3>{titulo}</h3>
                  <p>{texto}</p>
                </div>
              </Aparecer>
            </li>
          ))}
        </ol>
        <div className={estilos.destinos}>
          {DESTINOS.map(({ titulo, regra, resultado }, indice) => (
            <Aparecer key={titulo} atraso={indice * 90} className={estilos.destino}>
              <h3>{titulo}</h3>
              <p className={estilos.regra}>{regra}</p>
              <p>{resultado}</p>
            </Aparecer>
          ))}
        </div>
        <p className={secao.nota}>
          A comparação usa regras e semelhança de texto que a gestão consegue conferir, sem modelo
          de inteligência artificial e sem enviar o relato a serviço externo.
        </p>
      </div>
    </section>
  )
}

function SecaoDePrivacidade() {
  return (
    <section id="privacidade" className={secao.secao} aria-labelledby="titulo-privacidade">
      <div className={`conteudo ${estilos.colunas}`}>
        <Aparecer>
          <p className={secao.rotulo}>Privacidade</p>
          <h2 id="titulo-privacidade" className={secao.titulo}>
            Como usamos os seus dados
          </h2>
          <ul className={estilos.garantias}>
            {GARANTIAS_DE_PRIVACIDADE.map((garantia) => (
              <li key={garantia}>
                <Icone nome="escudo" tamanho={20} />
                {garantia}
              </li>
            ))}
          </ul>
        </Aparecer>
        <Aparecer atraso={120}>
          <p className={secao.rotulo}>Leitura honesta</p>
          <h2 className={secao.titulo}>O que o número não diz</h2>
          <ul className={estilos.garantias}>
            {LEITURAS_HONESTAS.map((leitura) => (
              <li key={leitura}>
                <Icone nome="informacao" tamanho={20} />
                {leitura}
              </li>
            ))}
          </ul>
        </Aparecer>
      </div>
    </section>
  )
}

export function PaginaComoFunciona() {
  useTituloDaPagina('Como funciona')

  return (
    <>
      <CabecalhoDaPagina
        rotulo="Como funciona"
        titulo="Do seu relato até a gestão, e de volta para você"
      >
        Quem pode ver o quê, como a plataforma evita duplicidade e o que ela faz para proteger quem
        relata.
      </CabecalhoDaPagina>
      <section className={secao.secao} aria-labelledby="titulo-passos">
        <div className="conteudo">
          <Aparecer>
            <p className={secao.rotulo}>Passo a passo</p>
            <h2 id="titulo-passos" className={secao.titulo}>
              Quatro passos, e você acompanha cada um
            </h2>
          </Aparecer>
          <PassosDoCidadao />
        </div>
      </section>
      <section className={`${secao.secao} ${secao.semTopo}`} aria-labelledby="titulo-acesso">
        <div className="conteudo">
          <Aparecer>
            <p className={secao.rotulo}>Quem vê o quê</p>
            <h2 id="titulo-acesso" className={secao.titulo}>
              Três níveis de acesso
            </h2>
            <p className={secao.abertura}>
              Com conta, você vê a rua e uma faixa de numeração de cada relato. O número exato e o
              texto escrito ficam só com a gestão, que usa essas informações para conferir
              duplicidade.
            </p>
          </Aparecer>
          <Aparecer>
            <TabelaDeAcesso />
          </Aparecer>
        </div>
      </section>
      <SecaoDoPenteFino />
      <SecaoDePrivacidade />
      <section className={estilos.chamada} aria-label="Criar conta">
        <div className={`conteudo ${estilos.chamadaInterna}`}>
          <p>Quer acompanhar o seu bairro?</p>
          <LinkDeBotao para="/cadastrar" variante="claro">
            Criar conta
          </LinkDeBotao>
        </div>
      </section>
    </>
  )
}
