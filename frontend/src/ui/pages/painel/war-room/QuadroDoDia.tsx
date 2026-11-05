import { useMemo, useState } from 'react'

import { useCatalogo } from '../../../../application/consultas/usePainel'
import { classeDoValor, faixasPorQuantis } from '../../../../domain/classes'
import {
  formatarDiaEMes,
  formatarNumero,
  formatarPorcentagem,
  nomeDoDiaDaSemana,
} from '../../../../domain/formatacao'
import { nomeDaCategoria, nomeDoOrgao } from '../../../../domain/nomes'
import type { FilaDoDia, QuadroDoDia as Quadro } from '../../../../domain/warRoom'
import { BarrasAgrupadas } from '../../../charts/BarrasAgrupadas'
import { BarrasHorizontais } from '../../../charts/BarrasHorizontais'
import { COR } from '../../../charts/estilo'
import { BarraNaCelula } from '../../../components/BarraNaCelula'
import { Cartao } from '../../../components/Cartao'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Medidor } from '../../../components/Medidor'
import { Tabela, type ColunaDaTabela } from '../../../components/Tabela'
import { LegendaDoMapa } from '../../../map/LegendaDoMapa'
import { MapaCoropletico, type ValorDoBairro } from '../../../map/MapaCoropletico'
import estilos from './PaginaWarRoom.module.css'

const NOTA_ALTA = 7
const NOTA_MAXIMA = 10
const ALERTA_DE_VARIACAO = 10
const ALTURA_DO_MAPA = 470
const SERIES = [
  { chave: 'entradas', rotulo: 'entraram', cor: COR.principal },
  { chave: 'atendidos', rotulo: 'atendidos', cor: COR.marinho },
]

function sinal(valor: number): string {
  return valor > 0 ? '+' : ''
}

function FaixaDoDia({ quadro }: { quadro: Quadro }) {
  const { entradas, dia } = quadro
  if (!entradas) {
    return <p className={estilos.semEntradas}>Sem entradas registradas neste dia.</p>
  }
  const diferenca = (entradas.entradas / Math.max(entradas.mediaDoDiaDaSemana, 1) - 1) * 100
  const saldo = entradas.entradas - entradas.atendidos
  const outras = entradas.camara + entradas.ouvidoria + entradas.defesaCivil
  const itens = [
    {
      rotulo: 'Entraram no 156',
      valor: formatarNumero(entradas.entradas),
      detalhe: `${sinal(diferenca)}${formatarPorcentagem(diferenca)} sobre a média de ${nomeDoDiaDaSemana(dia)}`,
    },
    {
      rotulo: 'Atendidos no 156',
      valor: formatarNumero(entradas.atendidos),
      detalhe: 'pela data do último movimento',
    },
    {
      rotulo: 'Saldo do dia',
      valor: `${sinal(saldo)}${formatarNumero(saldo)}`,
      detalhe: saldo > 0 ? 'a fila cresceu' : 'a fila diminuiu',
    },
    {
      rotulo: 'Outras portas',
      valor: formatarNumero(outras),
      detalhe: `Câmara ${formatarNumero(entradas.camara)} · Ouvidoria ${formatarNumero(entradas.ouvidoria)} · Defesa Civil ${formatarNumero(entradas.defesaCivil)}`,
    },
  ]
  return (
    <dl className={estilos.faixa}>
      {itens.map(({ rotulo, valor, detalhe }) => (
        <div key={rotulo}>
          <dt>{rotulo}</dt>
          <dd className="numero">{valor}</dd>
          <dd className={estilos.detalheDaFaixa}>{detalhe}</dd>
        </div>
      ))}
    </dl>
  )
}

function EstoqueDoDia({ quadro }: { quadro: Quadro }) {
  const { estoque } = quadro
  const { camara, ouvidoria } = estoque
  const pctAtrasados = estoque.abertos ? (estoque.atrasados / estoque.abertos) * 100 : 0
  const pctPrioritarios = estoque.classificaveis
    ? (estoque.prioritarios / estoque.classificaveis) * 100
    : 0
  const anteriores = estoque.entradasNos30Anteriores
  const variacao = anteriores ? (estoque.entradasNosUltimos30 / anteriores - 1) * 100 : null
  return (
    <GradeDeKpis compacta>
      <KpiCard
        rotulo="Pedidos abertos no 156"
        valor={formatarNumero(estoque.abertos)}
        contexto={`${formatarPorcentagem(pctAtrasados)} além do prazo típico`}
        ajuda="Pedidos que já tinham entrado e ainda não tinham sido atendidos nesta data."
        alerta
        visual={<Medidor porcentagem={pctAtrasados} rotulo="Parte dos abertos além do prazo" />}
      />
      <KpiCard
        rotulo={`Nota ${NOTA_ALTA} ou mais`}
        valor={formatarNumero(estoque.prioritarios)}
        contexto={`${formatarPorcentagem(pctPrioritarios, 1)} dos classificáveis`}
        ajuda="Pedidos abertos com nota de prioridade 7 ou mais no AHP: o primeiro lote a atender."
        visual={<Medidor porcentagem={pctPrioritarios} rotulo="Parte da fila com nota alta" />}
      />
      <KpiCard
        rotulo="Indicações sem resposta"
        valor={formatarNumero(camara.total)}
        contexto={`mediana de ${formatarNumero(camara.medianaDeDias ?? 0)} dias`}
        ajuda="Indicações já enviadas à Prefeitura e ainda sem resposta registrada nesta data. A mediana conta os dias desde o envio."
        alerta
      />
      <KpiCard
        rotulo="Ouvidoria além do prazo"
        valor={formatarNumero(ouvidoria.total)}
        contexto={`mediana de ${formatarNumero(ouvidoria.medianaDeDias ?? 0)} dias`}
        ajuda="Manifestações abertas cujo prazo legal de resposta já tinha passado. A mediana conta os dias além do prazo."
        alerta
      />
      <KpiCard
        rotulo={`Entrada em 30 dias, até ${formatarDiaEMes(estoque.fimDaJanela)}`}
        valor={formatarNumero(estoque.entradasNosUltimos30)}
        contexto={
          variacao === null
            ? 'sem os 30 dias anteriores'
            : `${sinal(variacao)}${formatarPorcentagem(variacao)} sobre os 30 dias anteriores`
        }
        ajuda="Pedidos que entraram no 156 nos 30 dias até a data, comparados com os 30 dias antes."
        alerta={variacao !== null && variacao > ALERTA_DE_VARIACAO}
      />
    </GradeDeKpis>
  )
}

function colunasDaFila(nomes: ReadonlyMap<string, string>): ColunaDaTabela<FilaDoDia>[] {
  return [
    {
      titulo: 'Nota',
      numerica: true,
      ajuda: 'Nota de prioridade de 0 a 10 pelo AHP. Maior, mais urgente.',
      valor: (item) => (
        <BarraNaCelula
          valor={item.nota}
          maximo={NOTA_MAXIMA}
          texto={formatarNumero(item.nota, 1)}
        />
      ),
    },
    { titulo: 'Serviço', valor: (item) => nomeDaCategoria(item.servico) },
    { titulo: 'Bairro', valor: (item) => nomes.get(item.bairroOficial ?? '') ?? 'não informado' },
    {
      titulo: 'Aberto há',
      numerica: true,
      valor: (item) => `${formatarNumero(item.idadeDias)} dias`,
    },
    {
      titulo: 'Anteriores',
      numerica: true,
      ajuda: 'Pedidos do mesmo serviço no mesmo endereço antes deste.',
      valor: (item) =>
        item.pedidosAnteriores === null ? 'sem número' : formatarNumero(item.pedidosAnteriores),
    },
  ]
}

interface Destaque {
  rotulo: string
  titulo: string
  detalhe: string
}

function montarDestaques(quadro: Quadro, nomes: ReadonlyMap<string, string>): Destaque[] {
  const { categorias, fila, estoque } = quadro
  const destaques: Destaque[] = []
  const categoria = categorias[0]
  if (categoria) {
    destaques.push({
      rotulo: 'Maior estoque atrasado',
      titulo: nomeDaCategoria(categoria.categoria),
      detalhe: `${formatarNumero(categoria.atrasados)} pedidos além do prazo típico`,
    })
  }
  const primeiro = fila[0]
  if (primeiro) {
    const bairro = nomes.get(primeiro.bairroOficial ?? '') ?? 'bairro não informado'
    destaques.push({
      rotulo: 'Primeiro da fila',
      titulo: nomeDaCategoria(primeiro.servico),
      detalhe: `${bairro}, aberto há ${formatarNumero(primeiro.idadeDias)} dias`,
    })
  }
  if (estoque.camara.temaComMais) {
    destaques.push({
      rotulo: 'Câmara sem resposta',
      titulo: nomeDaCategoria(estoque.camara.temaComMais),
      detalhe: `${formatarNumero(estoque.camara.temaQuantidade)} indicações`,
    })
  }
  if (estoque.ouvidoria.orgaoComMais) {
    destaques.push({
      rotulo: 'Ouvidoria além do prazo',
      titulo: nomeDoOrgao(estoque.ouvidoria.orgaoComMais),
      detalhe: `${formatarNumero(estoque.ouvidoria.orgaoQuantidade)} de ${formatarNumero(estoque.ouvidoria.total)} manifestações`,
    })
  }
  return destaques
}

function DestaquesDoDia({ destaques }: { destaques: readonly Destaque[] }) {
  return (
    <ul className={estilos.destaques} aria-label="Alertas do dia">
      {destaques.map(({ rotulo, titulo, detalhe }) => (
        <li key={rotulo} className={estilos.destaque}>
          <p className={estilos.rotuloDoDestaque}>{rotulo}</p>
          <p className={estilos.tituloDoDestaque}>{titulo}</p>
          <p className={estilos.detalheDoDestaque}>{detalhe}</p>
        </li>
      ))}
    </ul>
  )
}

function barrasDoDia(
  itens: readonly { nome: string; n: number }[],
  nome: (item: string) => string,
) {
  return itens.map((item) => ({
    chave: item.nome,
    rotulo: nome(item.nome),
    valor: item.n,
    texto: formatarNumero(item.n),
    detalhe: 'pedidos neste dia',
  }))
}

export function QuadroDoDia({ quadro }: { quadro: Quadro }) {
  const [escolhido, definirEscolhido] = useState<string | null>(null)
  const { dados: catalogo } = useCatalogo()
  const nomes = useMemo(
    () => new Map(catalogo?.bairros.map((bairro) => [bairro.bairroOficial, bairro.nome])),
    [catalogo],
  )
  const faixas = useMemo(
    () => faixasPorQuantis(quadro.atrasoPorBairro.map((item) => item.atrasados)),
    [quadro.atrasoPorBairro],
  )
  const valores = useMemo(() => {
    const mapa = new Map<string, ValorDoBairro>()
    quadro.atrasoPorBairro.forEach(({ bairroOficial, atrasados }) => {
      const nome = nomes.get(bairroOficial) ?? bairroOficial
      mapa.set(nome, {
        classe: classeDoValor(atrasados, faixas),
        emDestaque: true,
        dica: `${nome}\n${formatarNumero(atrasados)} pedidos atrasados`,
      })
    })
    return mapa
  }, [quadro.atrasoPorBairro, nomes, faixas])
  const maximoDeAtraso = Math.max(...quadro.categorias.map((item) => item.atrasados), 1)
  const ranking = useMemo(
    () => [...quadro.atrasoPorBairro].sort((a, b) => b.atrasados - a.atrasados),
    [quadro.atrasoPorBairro],
  )
  const posicao = ranking.findIndex((item) => (nomes.get(item.bairroOficial) ?? '') === escolhido)
  const bairroEscolhido = ranking[posicao]
  const barrasDeEntrada = [
    ...barrasDoDia(quadro.categoriasDoDia, nomeDaCategoria),
    ...barrasDoDia(quadro.bairrosDoDia, (nome) => nomes.get(nome) ?? nome),
  ]

  return (
    <>
      <FaixaDoDia quadro={quadro} />
      <EstoqueDoDia quadro={quadro} />
      <DestaquesDoDia destaques={montarDestaques(quadro, nomes)} />
      <div className={estilos.mapaEFila}>
        <Cartao
          titulo="Onde o estoque atrasado está"
          ajuda="Quanto mais escuro o bairro, mais pedidos abertos já passaram do prazo típico da categoria. Clique num bairro."
          nota={
            bairroEscolhido
              ? `${escolhido}: ${formatarNumero(bairroEscolhido.atrasados)} pedidos atrasados, ${posicao + 1}º da cidade.`
              : 'Clique num bairro para ver a posição dele.'
          }
        >
          <MapaCoropletico
            rotulo="Pedidos do 156 abertos além do prazo típico, por bairro. As categorias com mais atraso estão abaixo."
            valores={valores}
            altura={ALTURA_DO_MAPA}
            selecionado={escolhido}
            aoClicar={(nome) => definirEscolhido((atual) => (atual === nome ? null : nome))}
          />
          <LegendaDoMapa titulo="pedidos atrasados" faixas={faixas} casas={0} />
        </Cartao>
        <Cartao
          titulo={`Fila do dia: 12 de ${formatarNumero(quadro.estoque.classificaveis)} pedidos abertos`}
          ajuda="Os pedidos abertos nesta data de maior nota no AHP: por onde começar."
        >
          <Tabela
            legenda="Fila do dia"
            colunas={colunasDaFila(nomes)}
            linhas={quadro.fila}
            chave={(_, indice) => String(indice)}
          />
        </Cartao>
      </div>
      <div className={barrasDeEntrada.length > 0 ? estilos.tresColunas : estilos.duasColunas}>
        <Cartao titulo="156, por dia" ajuda="Pedidos que entraram e foram atendidos em cada dia.">
          <BarrasAgrupadas
            dados={quadro.serie.map((ponto) => ({ ...ponto, dia: formatarDiaEMes(ponto.data) }))}
            eixo="dia"
            series={SERIES}
          />
        </Cartao>
        <Cartao
          titulo="Categorias com mais atraso"
          ajuda="Pedidos abertos além do prazo típico, por categoria, e a parte dos abertos que já atrasou."
        >
          <BarrasHorizontais
            dados={quadro.categorias.map((item) => ({
              chave: item.categoria,
              rotulo: nomeDaCategoria(item.categoria),
              valor: item.atrasados,
              texto: formatarNumero(item.atrasados),
              detalhe: `pedidos atrasados, ${formatarPorcentagem((item.atrasados / Math.max(item.abertos, 1)) * 100)} dos abertos`,
              cor: COR.marinho,
            }))}
            maximo={maximoDeAtraso}
            larguraDoRotulo={130}
          />
        </Cartao>
        {barrasDeEntrada.length > 0 && (
          <Cartao
            titulo="O que mais entrou neste dia"
            ajuda="Categorias e bairros com mais pedidos registrados nesta data."
          >
            <BarrasHorizontais
              dados={barrasDeEntrada}
              maximo={Math.max(...barrasDeEntrada.map((barra) => barra.valor), 1)}
              larguraDoRotulo={130}
              alturaDaLinha={28}
            />
          </Cartao>
        )}
      </div>
    </>
  )
}
