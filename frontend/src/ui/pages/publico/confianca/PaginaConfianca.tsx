import type { CSSProperties } from 'react'

import { formatarNumero } from '../../../../domain/formatacao'
import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import {
  CAMADAS_DO_PENTE_FINO,
  FONTES_DE_DADOS,
  GARANTIAS_DE_PRIVACIDADE,
  LEITURAS_HONESTAS,
  NUMEROS_DA_BASE,
} from '../conteudo'
import secao from '../Secao.module.css'
import estilos from './PaginaConfianca.module.css'

const TOTAL_DE_REGISTROS = FONTES_DE_DADOS.reduce((total, fonte) => total + fonte.registros, 0)

const DESTINOS = [
  {
    titulo: 'Igual',
    regra: 'Mesmo endereço com número, mesmo serviço, até 7 dias.',
    resultado: 'Soma sozinho. Vira uma ocorrência com mais de um relato.',
  },
  {
    titulo: 'Parecido',
    regra: 'Rua, número ou serviço próximos, menos de 30 dias.',
    resultado: 'Vai para a gestão, lado a lado, com o motivo escrito.',
  },
  {
    titulo: 'Diferente',
    regra: 'Outro lugar, outro tema ou 30 dias ou mais depois.',
    resultado: 'Fica como ocorrência própria. Se voltou, é reincidência.',
  },
] as const

function SecaoDoPenteFino() {
  return (
    <section className={secao.secao} aria-labelledby="titulo-pente-fino">
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>Pente fino</p>
          <h2 id="titulo-pente-fino" className={secao.titulo}>
            A mesma demanda não entra duas vezes
          </h2>
          <p className={secao.abertura}>
            Vale para quem preenche o formulário e para quem importa um arquivo. Toda importação
            manual é comparada com os relatos, e todo pacote de relatos é comparado com a base. Se
            houver coincidência, a carga para até alguém decidir.
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
          de inteligência artificial e sem enviar o relato a serviço externo. As fontes oficiais não
          têm uma chave em comum, por isso a comparação entre canais depende do endereço: linha sem
          endereço é contada à parte e aparece no relatório da importação.
        </p>
      </div>
    </section>
  )
}

function SecaoDasFontes() {
  return (
    <section className={`${secao.secao} ${secao.fundoClaro}`} aria-labelledby="titulo-fontes">
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>Fontes</p>
          <h2 id="titulo-fontes" className={secao.titulo}>
            De onde vêm os {formatarNumero(NUMEROS_DA_BASE[0]?.valor ?? 0)} registros
          </h2>
        </Aparecer>
        <Aparecer className={estilos.composicao}>
          {FONTES_DE_DADOS.map(({ nome, registros, cor }) => (
            <span
              key={nome}
              title={`${nome}: ${formatarNumero(registros)}`}
              style={
                {
                  '--tamanho': `${(registros / TOTAL_DE_REGISTROS) * 100}%`,
                  background: cor,
                } as CSSProperties
              }
            />
          ))}
        </Aparecer>
        <Aparecer className={estilos.rolagem}>
          <table className={estilos.tabela}>
            <caption className="visualmente-oculto">
              Fontes da base, com o período e a quantidade de registros
            </caption>
            <thead>
              <tr>
                <th scope="col">Fonte</th>
                <th scope="col">O que cada registro representa</th>
                <th scope="col">Período</th>
                <th scope="col" className={estilos.numerica}>
                  Registros
                </th>
              </tr>
            </thead>
            <tbody>
              {FONTES_DE_DADOS.map(({ nome, registra, periodo, registros, cor }) => (
                <tr key={nome}>
                  <th scope="row">
                    <span className={estilos.marca} style={{ background: cor }} />
                    {nome}
                  </th>
                  <td>{registra}</td>
                  <td>{periodo}</td>
                  <td className={`numero ${estilos.numerica}`}>{formatarNumero(registros)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th scope="row" colSpan={3}>
                  Total
                </th>
                <td className={`numero ${estilos.numerica}`}>
                  {formatarNumero(TOTAL_DE_REGISTROS)}
                </td>
              </tr>
            </tfoot>
          </table>
        </Aparecer>
        <p className={secao.nota}>
          Fonte: Portal de Dados Abertos do Recife (licença ODbL), sistema SAGL da Câmara Municipal
          do Recife e Censo 2022 do IBGE. A SEDEC vem da cópia de 09/03/2024 guardada pelo Internet
          Archive.
        </p>
      </div>
    </section>
  )
}

function SecaoDePrivacidade() {
  return (
    <section className={secao.secao} aria-labelledby="titulo-privacidade">
      <div className={`conteudo ${estilos.colunas}`}>
        <Aparecer>
          <p className={secao.rotulo}>Privacidade</p>
          <h2 id="titulo-privacidade" className={secao.titulo}>
            O que protegemos
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

export function PaginaConfianca() {
  useTituloDaPagina('Dados e confiança')

  return (
    <>
      <CabecalhoDaPagina rotulo="Dados e confiança" titulo="Um número só vale se der para conferir">
        Como a plataforma evita duplicidade, de onde vem cada dado e o que ela faz para proteger
        quem relata.
      </CabecalhoDaPagina>
      <SecaoDoPenteFino />
      <SecaoDasFontes />
      <SecaoDePrivacidade />
      <section className={estilos.chamada} aria-label="Enviar um relato">
        <div className={`conteudo ${estilos.chamadaInterna}`}>
          <p>Viu um problema na sua rua?</p>
          <LinkDeBotao para="/contribuir" variante="claro">
            Relatar um problema
          </LinkDeBotao>
        </div>
      </section>
    </>
  )
}
