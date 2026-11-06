import type { ReactNode } from 'react'
import { Link } from 'react-router'

import { Aparecer } from '../../../components/Aparecer'
import { Icone } from '../../../components/Icone'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import { PROBLEMAS, RESULTADOS_PEDIDOS, type ProblemaResolvido } from '../conteudo'
import secao from '../Secao.module.css'
import {
  DestinoDasIndicacoes,
  FunilDoRetorno,
  IntervalosDaRepeticao,
  PrazoPorAno,
} from './Evidencias'
import estilos from './PaginaOQueMuda.module.css'

const EVIDENCIAS: Readonly<Record<string, ReactNode>> = {
  repeticao: <IntervalosDaRepeticao />,
  retorno: <FunilDoRetorno />,
  prazos: <PrazoPorAno />,
  destino: <DestinoDasIndicacoes />,
}

function LinhaDoProblema({ problema }: { problema: ProblemaResolvido }) {
  const { chave, icone, titulo, antes, agora, tela, caminho } = problema
  const evidencia = EVIDENCIAS[chave]

  return (
    <article className={estilos.problema}>
      <Aparecer>
        <h2 className={estilos.tituloDoProblema}>
          <span className={estilos.icone}>
            <Icone nome={icone} tamanho={24} />
          </span>
          {titulo}
        </h2>
      </Aparecer>
      <div className={estilos.comparacao}>
        <Aparecer className={estilos.antes}>
          <h3>Antes</h3>
          <p>{antes}</p>
        </Aparecer>
        <Aparecer atraso={120} className={estilos.agora}>
          <h3>Com o RecifeView</h3>
          <p>{agora}</p>
          <Link to={caminho} className={estilos.tela}>
            Tela: {tela}
            <Icone nome="seta" tamanho={16} />
          </Link>
        </Aparecer>
      </div>
      {evidencia && <Aparecer className={estilos.evidencia}>{evidencia}</Aparecer>}
    </article>
  )
}

export function PaginaOQueMuda() {
  useTituloDaPagina('O que muda')

  return (
    <>
      <CabecalhoDaPagina
        rotulo="O que muda"
        titulo="Os problemas de antes e o que muda com o painel"
      >
        A entrada dos pedidos já funcionava. A perda acontecia depois dela: dados separados, retorno
        sem registro e repetição que ninguém via.
      </CabecalhoDaPagina>
      <div className={`conteudo ${estilos.lista}`}>
        {PROBLEMAS.map((problema) => (
          <LinhaDoProblema key={problema.chave} problema={problema} />
        ))}
      </div>
      <section
        className={`${secao.secao} ${secao.fundoClaro}`}
        aria-labelledby="titulo-resultados-pedidos"
      >
        <div className="conteudo">
          <Aparecer>
            <p className={secao.rotulo}>O que o desafio do Conecta Recife pede</p>
            <h2 id="titulo-resultados-pedidos" className={secao.titulo}>
              Cada resultado esperado tem um lugar no painel
            </h2>
          </Aparecer>
          <dl className={estilos.resultados}>
            {RESULTADOS_PEDIDOS.map(({ pedido, resposta }, indice) => (
              <Aparecer key={pedido} atraso={indice * 80} className={estilos.resultado}>
                <dt>{pedido}</dt>
                <dd>{resposta}</dd>
              </Aparecer>
            ))}
          </dl>
          <p className={secao.nota}>
            O painel organiza as evidências. A decisão continua com a gestão e com os critérios da
            Prefeitura.
          </p>
        </div>
      </section>
    </>
  )
}
