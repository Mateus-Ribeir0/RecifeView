import type { ReactNode } from 'react'

import { formatarNumero } from '../../../../domain/formatacao'
import { Aparecer } from '../../../components/Aparecer'
import { Icone, type NomeDoIcone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import { FONTES_DE_DADOS, NOTA_DA_BASE } from '../conteudo'
import { FaixaDeNumeros } from '../inicio/FaixaDeNumeros'
import secao from '../Secao.module.css'
import {
  DestinoDasIndicacoes,
  FunilDoRetorno,
  IntervalosDaRepeticao,
  PrazoPorAno,
} from './Evidencias'
import estilos from './PaginaCidadeEmNumeros.module.css'

interface Achado {
  icone: NomeDoIcone
  titulo: string
  texto: string
  grafico: ReactNode
}

const ACHADOS: readonly Achado[] = [
  {
    icone: 'repetir',
    titulo: 'O problema volta para o mesmo endereço',
    texto:
      'Mais da metade dos pedidos à Central 156 com número no endereço cai num lugar e serviço que já tinham sido pedidos. Na maioria das vezes, o novo pedido vem um mês ou mais depois: o problema voltou.',
    grafico: <IntervalosDaRepeticao />,
  },
  {
    icone: 'retorno',
    titulo: 'A resposta nem sempre fica registrada',
    texto:
      'Quase todas as indicações dos vereadores chegam à Prefeitura, mas poucas têm uma resposta registrada. Isso não quer dizer que não foram atendidas, e sim que o retorno se perde no caminho.',
    grafico: <FunilDoRetorno />,
  },
  {
    icone: 'relogio',
    titulo: 'A demora está nos pedidos mais lentos',
    texto:
      'O pedido típico é atendido em poucos dias. Mas os 10% mais demorados passaram a levar o dobro do tempo nos últimos anos.',
    grafico: <PrazoPorAno />,
  },
  {
    icone: 'filtro',
    titulo: 'Alguns temas passam por vários órgãos',
    texto:
      'Em áreas de risco, escadarias, praças e pavimentação, a indicação se divide entre órgãos diferentes, o que ajuda a explicar por que alguns casos demoram.',
    grafico: <DestinoDasIndicacoes />,
  },
]

const TOTAL_DE_REGISTROS = FONTES_DE_DADOS.reduce((total, fonte) => total + fonte.registros, 0)

function TabelaDeFontes() {
  return (
    <div className={estilos.rolagem}>
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
            <td className={`numero ${estilos.numerica}`}>{formatarNumero(TOTAL_DE_REGISTROS)}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

export function PaginaCidadeEmNumeros() {
  useTituloDaPagina('A cidade em números')

  return (
    <>
      <CabecalhoDaPagina
        rotulo="A cidade em números"
        titulo="O que os dados abertos mostram sobre o Recife"
      >
        Quinze anos de pedidos à Prefeitura, de cinco fontes públicas, organizados por bairro,
        serviço e período. Os números são os mesmos que a gestão vê.
      </CabecalhoDaPagina>
      <FaixaDeNumeros />
      <div className={`conteudo ${estilos.achados}`}>
        {ACHADOS.map(({ icone, titulo, texto, grafico }) => (
          <article key={titulo} className={estilos.achado}>
            <Aparecer className={estilos.textoDoAchado}>
              <span className={estilos.icone}>
                <Icone nome={icone} tamanho={24} />
              </span>
              <h2>{titulo}</h2>
              <p>{texto}</p>
            </Aparecer>
            <Aparecer atraso={120}>{grafico}</Aparecer>
          </article>
        ))}
      </div>
      <section className={`${secao.secao} ${secao.fundoClaro}`} aria-labelledby="titulo-fontes">
        <div className="conteudo">
          <Aparecer>
            <p className={secao.rotulo}>Fontes</p>
            <h2 id="titulo-fontes" className={secao.titulo}>
              De onde vêm os {formatarNumero(TOTAL_DE_REGISTROS)} registros
            </h2>
          </Aparecer>
          <Aparecer>
            <TabelaDeFontes />
          </Aparecer>
          <p className={secao.nota}>
            {NOTA_DA_BASE} A SEDEC vem da cópia de 09/03/2024 guardada pelo Internet Archive.
          </p>
        </div>
      </section>
      <section className={estilos.chamada} aria-label="Ver o seu bairro">
        <div className={`conteudo ${estilos.chamadaInterna}`}>
          <p>Quer ver estes números para o seu bairro?</p>
          <LinkDeBotao para="/cadastrar" variante="claro">
            Criar conta
          </LinkDeBotao>
        </div>
      </section>
    </>
  )
}
