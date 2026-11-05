import { useState } from 'react'

import { useCatalogo, useRecorrencias } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import { formatarNumero, formatarPeriodo, formatarPorcentagem } from '../../../../domain/formatacao'
import { nomeDaCategoria } from '../../../../domain/nomes'
import type { IntervalosDeRepeticao, PontoCronico, Recorrencias } from '../../../../domain/painel'
import { BarrasHorizontais } from '../../../charts/BarrasHorizontais'
import { BarrasVerticais } from '../../../charts/BarrasVerticais'
import { COR } from '../../../charts/estilo'
import { Alternador } from '../../../components/Alternador'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Colunas, Secao } from '../../../components/Secao'
import { Tabela, type ColunaDaTabela } from '../../../components/Tabela'

const DEFINICAO =
  'Definição: 156 de 2015 a 2025, só endereços com número; chave = local e serviço (o local é um pseudônimo do endereço, que não aparece no painel).'

function pctDe(parte: number, total: number): number {
  return total ? (parte / total) * 100 : 0
}

function colunasDosIntervalos(intervalos: IntervalosDeRepeticao) {
  const faixas = [
    { rotulo: 'Duplicidade\naté 7 dias', n: intervalos.duplicidade, cor: COR.medio },
    { rotulo: 'Intermediário\n8 a 29 dias', n: intervalos.intermediario, cor: COR.contexto },
    { rotulo: 'Reincidência\n30 dias ou mais', n: intervalos.reincidencia, cor: COR.marinho },
  ]
  return faixas.map(({ rotulo, n, cor }) => ({
    rotulo,
    valor: pctDe(n, intervalos.total),
    texto: formatarPorcentagem(pctDe(n, intervalos.total)),
    detalhe: 'das repetições',
    cor,
  }))
}

function colunasDosPontos(nomes: ReadonlyMap<string, string>): ColunaDaTabela<PontoCronico>[] {
  return [
    {
      titulo: 'Bairro',
      valor: (ponto) => nomes.get(ponto.bairroOficial ?? '') ?? 'não informado',
    },
    { titulo: 'Categoria', valor: (ponto) => nomeDaCategoria(ponto.categoria) },
    { titulo: 'Serviço', valor: (ponto) => nomeDaCategoria(ponto.servico) },
    {
      titulo: 'Pedidos',
      numerica: true,
      ajuda: 'Pedidos do mesmo serviço neste mesmo endereço.',
      valor: (ponto) => formatarNumero(ponto.pedidos),
    },
    {
      titulo: 'Dias com pedido',
      numerica: true,
      ajuda: 'Dias diferentes com pedido: separa problema que volta de pedido em dobro.',
      valor: (ponto) => formatarNumero(ponto.diasDistintos),
    },
    {
      titulo: 'Período',
      numerica: true,
      ajuda: 'Primeiro e último ano com pedido.',
      valor: (ponto) => formatarPeriodo(ponto.primeiroAno, ponto.ultimoAno),
    },
  ]
}

interface ConteudoProps {
  dados: Recorrencias
  nota: string
}

function ConteudoDaReincidencia({ dados, nota }: ConteudoProps) {
  const [escolhida, definirEscolhida] = useState<string | null>(null)
  const { dados: catalogo } = useCatalogo()
  const nomes = new Map(catalogo?.bairros.map((bairro) => [bairro.bairroOficial, bairro.nome]))
  const categoria = dados.porCategoria.find((item) => item.categoria === escolhida)
  const intervalos = categoria?.intervalos ?? dados.intervalos
  const recorte = categoria ? nomeDaCategoria(categoria.categoria) : 'todas as categorias'

  return (
    <>
      <GradeDeKpis>
        <KpiCard
          rotulo="Em local repetido"
          valor={formatarPorcentagem(dados.pctRepetidos, 1)}
          contexto={`de ${formatarNumero(dados.pedidos)} pedidos`}
          ajuda="Pedidos cujo local e serviço aparecem 2 ou mais vezes entre 2015 e 2025."
        />
        <KpiCard
          rotulo="O problema voltou"
          valor={formatarPorcentagem(pctDe(dados.intervalos.reincidencia, dados.intervalos.total))}
          contexto="30 dias ou mais depois"
          ajuda="Entre os pedidos que repetem um anterior, a parte em que o intervalo foi de 30 dias ou mais."
        />
        <KpiCard
          rotulo="Pedido em dobro"
          valor={formatarPorcentagem(pctDe(dados.intervalos.duplicidade, dados.intervalos.total))}
          contexto="até 7 dias depois"
          ajuda="Repetições em até 7 dias: provável duplicidade."
        />
        <KpiCard
          rotulo="Pontos crônicos"
          valor={formatarNumero(dados.pontosCronicos)}
          contexto="locais com 10 ou mais pedidos"
          ajuda="Locais e serviço com 10 pedidos ou mais na janela 2015 a 2025, ativos no período escolhido."
        />
      </GradeDeKpis>
      <Secao
        titulo="Onde mais se repete, e como"
        ajuda="Que categorias mais repetem pedido no mesmo local e quanto tempo passa entre um pedido e outro."
      >
        <Colunas>
          <Cartao
            titulo="% dos pedidos em local repetido, por categoria"
            ajuda="Clique numa barra para ver o intervalo dela."
            leitura={`Categorias com ${formatarNumero(dados.minimoPorCategoria)} pedidos ou mais no recorte. Clique numa barra para ver, ao lado, como os pedidos dela se repetem.`}
            nota={nota}
          >
            <BarrasHorizontais
              dados={dados.porCategoria.map((item) => ({
                chave: item.categoria,
                rotulo: nomeDaCategoria(item.categoria),
                valor: item.pctRepetidos,
                texto: formatarPorcentagem(item.pctRepetidos),
                detalhe: `em local repetido, de ${formatarNumero(item.pedidos)} pedidos`,
              }))}
              maximo={100}
              selecionada={escolhida}
              aoSelecionar={definirEscolhida}
              alturaDaLinha={26}
            />
          </Cartao>
          <Cartao
            titulo={`Intervalo até o pedido anterior no mesmo local: ${recorte}`}
            ajuda="Dias entre um pedido e o anterior no mesmo local: até 7 é pedido em dobro; 30 ou mais, o problema voltou."
            leitura="Duplicidade se resolve na triagem. Reincidência é outro problema: o serviço foi feito e não durou, ou não foi feito."
            nota={nota}
          >
            <BarrasVerticais
              dados={colunasDosIntervalos(intervalos)}
              rotuloDoEixo="% das repetições"
              maximo={100}
              larguraDaBarra={56}
            />
          </Cartao>
        </Colunas>
      </Secao>
      <Secao
        titulo="Pontos crônicos"
        ajuda="Endereços com muitos pedidos do mesmo serviço. O endereço não é mostrado, por privacidade."
      >
        <Cartao
          titulo={`Os ${dados.listaDePontos.length} locais com mais pedidos no recorte`}
          leitura="Cada linha é um endereço com muitos pedidos do mesmo serviço; o endereço não é mostrado. Um ponto com dezenas de pedidos pede uma solução definitiva, não mais um atendimento. Os primeiros, com centenas de pedidos, provavelmente são endereços genéricos ou circuitos inteiros de iluminação."
        >
          <Tabela
            legenda="Pontos crônicos do 156"
            colunas={colunasDosPontos(nomes)}
            linhas={dados.listaDePontos}
            chave={(_, indice) => String(indice)}
            altura={380}
          />
        </Cartao>
      </Secao>
    </>
  )
}

export function PaginaReincidencia() {
  const { filtros } = useFiltrosGlobais()
  const [semGenerico, definirSemGenerico] = useState(false)
  const consulta = useRecorrencias(filtros, semGenerico)
  const periodo = formatarPeriodo(filtros.anoInicio, filtros.anoFim)

  return (
    <>
      <CabecalhoDaTela
        titulo="Reincidência"
        fontes={['156_EMLURB']}
        ignorados={[DEFINICAO]}
        atualizando={consulta.atualizando}
      >
        Repetir não é duplicar. Boa parte dos pedidos do 156 cai num local e serviço que já teve
        pedido, e na maioria das vezes o problema voltou semanas ou meses depois. Um ponto com 100
        pedidos é um problema, não cem.
      </CabecalhoDaTela>
      <Alternador
        rotulo="Tirar da conta os endereços genéricos"
        ajuda="Alguns locais somam centenas de pedidos do mesmo serviço em vários anos. Quase certamente é um endereço genérico ou um circuito inteiro. Ligado, os pedidos em locais acima do p99 deixam de contar como repetidos."
        ligado={semGenerico}
        aoMudar={definirSemGenerico}
      />
      <EstadoDaConsulta
        consulta={consulta}
        estaVazia={({ dados }) => dados.pedidos === 0}
        mensagemDeVazio="Sem pedidos do 156 para estes filtros. A reincidência é medida de 2015 a 2025."
      >
        {({ dados, meta }) => (
          <ConteudoDaReincidencia
            dados={dados}
            nota={`Fonte: Central 156. Período: ${periodo}. n = ${formatarNumero(meta.n)}.`}
          />
        )}
      </EstadoDaConsulta>
    </>
  )
}
