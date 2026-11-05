import { useMemo } from 'react'

import { useCatalogo } from '../../../../application/consultas/usePainel'
import { classeDoValor, faixasPorQuantis } from '../../../../domain/classes'
import {
  formatarData,
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
import { Cartao } from '../../../components/Cartao'
import { Tabela, type ColunaDaTabela } from '../../../components/Tabela'
import { LegendaDoMapa } from '../../../map/LegendaDoMapa'
import { MapaCoropletico, type ValorDoBairro } from '../../../map/MapaCoropletico'
import estilos from './PaginaWarRoom.module.css'
import { Placa } from './Placa'

const NOTA_ALTA = 7
const ALERTA_DE_ENTRADAS = 25
const ALERTA_DE_VARIACAO = 10
const SERIES = [
  { chave: 'entradas', rotulo: 'entraram', cor: COR.principal },
  { chave: 'atendidos', rotulo: 'atendidos', cor: COR.marinho },
]

function sinal(valor: number): string {
  return valor > 0 ? '+' : ''
}

function PlacasDoDia({ quadro }: { quadro: Quadro }) {
  const { entradas, dia } = quadro
  if (!entradas) {
    return (
      <p className={estilos.aviso}>
        Sem entradas registradas neste dia. Os números de estoque abaixo continuam valendo para a
        data.
      </p>
    )
  }
  const diferenca = (entradas.entradas / Math.max(entradas.mediaDoDiaDaSemana, 1) - 1) * 100
  const saldo = entradas.entradas - entradas.atendidos
  const outras = entradas.camara + entradas.ouvidoria + entradas.defesaCivil
  return (
    <div className={estilos.placas}>
      <Placa
        rotulo="Entraram no 156 neste dia"
        valor={formatarNumero(entradas.entradas)}
        ajuda="Pedidos registrados no 156 nesta data."
        alerta={diferenca > ALERTA_DE_ENTRADAS}
      >
        {sinal(diferenca)}
        {formatarPorcentagem(diferenca)} sobre a média de {nomeDoDiaDaSemana(dia)}
      </Placa>
      <Placa
        rotulo="Atendidos no 156 neste dia"
        valor={formatarNumero(entradas.atendidos)}
        ajuda="Pedidos marcados como atendidos nesta data, de qualquer data de entrada."
      >
        pela data do último movimento
      </Placa>
      <Placa
        rotulo="Saldo do dia"
        valor={`${sinal(saldo)}${formatarNumero(saldo)}`}
        ajuda="Entradas menos atendimentos: positivo, a fila cresceu."
        alerta={saldo > 0}
      >
        {saldo > 0 ? 'a fila cresceu' : 'a fila diminuiu'}
      </Placa>
      <Placa
        rotulo="Outras portas neste dia"
        valor={formatarNumero(outras)}
        ajuda="Registros que entraram nesta data pela Câmara, pela Ouvidoria e pela Defesa Civil."
      >
        Câmara {formatarNumero(entradas.camara)} · Ouvidoria {formatarNumero(entradas.ouvidoria)} ·
        Defesa Civil {formatarNumero(entradas.defesaCivil)}
      </Placa>
    </div>
  )
}

function PlacasDoEstoque({ quadro }: { quadro: Quadro }) {
  const { estoque } = quadro
  const { camara, ouvidoria } = estoque
  const pctAtrasados = estoque.abertos ? (estoque.atrasados / estoque.abertos) * 100 : 0
  const pctPrioritarios = estoque.classificaveis
    ? (estoque.prioritarios / estoque.classificaveis) * 100
    : 0
  const anteriores = estoque.entradasNos30Anteriores
  const variacao = anteriores ? (estoque.entradasNosUltimos30 / anteriores - 1) * 100 : null
  return (
    <div className={estilos.placas}>
      <Placa
        rotulo="Pedidos abertos no 156"
        valor={formatarNumero(estoque.abertos)}
        ajuda="Pedidos que já tinham entrado e ainda não tinham sido atendidos nesta data."
        alerta
      >
        {formatarPorcentagem(pctAtrasados)} além do prazo típico
      </Placa>
      <Placa
        rotulo={`Fila prioritária (nota ${NOTA_ALTA} ou mais)`}
        valor={formatarNumero(estoque.prioritarios)}
        ajuda="Pedidos abertos com nota de prioridade 7 ou mais no AHP: o primeiro lote a atender."
      >
        {formatarPorcentagem(pctPrioritarios, 1)} dos classificáveis
      </Placa>
      <Placa
        rotulo="Indicações sem resposta"
        valor={formatarNumero(camara.total)}
        ajuda="Indicações já enviadas à Prefeitura e ainda sem resposta registrada nesta data."
        alerta
      >
        mediana de {formatarNumero(camara.medianaDeDias ?? 0)} dias desde o envio
      </Placa>
      <Placa
        rotulo="Ouvidoria além do prazo"
        valor={formatarNumero(ouvidoria.total)}
        ajuda="Manifestações abertas cujo prazo legal de resposta já tinha passado."
        alerta
      >
        mediana de {formatarNumero(ouvidoria.medianaDeDias ?? 0)} dias além do prazo legal
      </Placa>
      <Placa
        rotulo={`Entrada no 156, 30 dias até ${formatarDiaEMes(estoque.fimDaJanela)}`}
        valor={formatarNumero(estoque.entradasNosUltimos30)}
        ajuda="Pedidos que entraram no 156 nos 30 dias até a data, comparados com os 30 dias antes."
        alerta={variacao !== null && variacao > ALERTA_DE_VARIACAO}
      >
        {variacao === null
          ? 'sem os 30 dias anteriores para comparar'
          : `${sinal(variacao)}${formatarPorcentagem(variacao)} sobre os 30 dias anteriores`}
      </Placa>
    </div>
  )
}

function colunasDaFila(nomes: ReadonlyMap<string, string>): ColunaDaTabela<FilaDoDia>[] {
  return [
    {
      titulo: 'Nota',
      numerica: true,
      ajuda: 'Nota de prioridade de 0 a 10 pelo AHP. Maior, mais urgente.',
      valor: (item) => formatarNumero(item.nota, 1),
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

function montarAlertas(quadro: Quadro, nomes: ReadonlyMap<string, string>): string[] {
  const { categorias, fila, estoque, entradas, dia } = quadro
  const alertas: string[] = []
  const categoria = categorias[0]
  if (categoria) {
    alertas.push(
      `${nomeDaCategoria(categoria.categoria)} tem ${formatarNumero(categoria.atrasados)} pedidos abertos além do prazo típico, o maior estoque atrasado da cidade.`,
    )
  }
  const primeiro = fila[0]
  if (primeiro) {
    const quantos = estoque.comNotaMuitoAlta
    const inicio = quantos
      ? `${formatarNumero(quantos)} ${quantos > 1 ? 'pedidos têm' : 'pedido tem'} nota 9 ou mais`
      : 'Nenhum pedido tem nota 9 ou mais'
    const bairro = nomes.get(primeiro.bairroOficial ?? '') ?? 'bairro não informado'
    alertas.push(
      `${inicio}; o primeiro da fila é ${nomeDaCategoria(primeiro.servico).toLowerCase()} em ${bairro}, aberto há ${formatarNumero(primeiro.idadeDias)} dias.`,
    )
  }
  if (entradas?.entradas) {
    const diferenca = (entradas.entradas / Math.max(entradas.mediaDoDiaDaSemana, 1) - 1) * 100
    alertas.push(
      `Entraram ${formatarNumero(entradas.entradas)} pedidos no 156 neste dia, ${diferenca >= 0 ? 'acima' : 'abaixo'} da média de ${nomeDoDiaDaSemana(dia)} (${formatarPorcentagem(Math.abs(diferenca))}).`,
    )
  }
  if (estoque.camara.temaComMais) {
    alertas.push(
      `Na Câmara, ${nomeDaCategoria(estoque.camara.temaComMais).toLowerCase()} lidera as indicações sem resposta (${formatarNumero(estoque.camara.temaQuantidade)}).`,
    )
  }
  if (estoque.ouvidoria.orgaoComMais) {
    alertas.push(
      `Na Ouvidoria, ${nomeDoOrgao(estoque.ouvidoria.orgaoComMais)} concentra ${formatarNumero(estoque.ouvidoria.orgaoQuantidade)} das ${formatarNumero(estoque.ouvidoria.total)} manifestações além do prazo.`,
    )
  }
  return alertas
}

export function QuadroDoDia({ quadro }: { quadro: Quadro }) {
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

  return (
    <>
      <PlacasDoDia quadro={quadro} />
      <PlacasDoEstoque quadro={quadro} />
      <div className={estilos.duasColunas}>
        <Cartao
          titulo="Onde o estoque atrasado está"
          ajuda="Quanto mais escuro o bairro, mais pedidos abertos já passaram do prazo típico da categoria."
        >
          <MapaCoropletico
            rotulo="Pedidos do 156 abertos além do prazo típico, por bairro. Os maiores estão nas categorias e nos alertas ao lado."
            valores={valores}
            altura={430}
          />
          <LegendaDoMapa titulo="pedidos atrasados" faixas={faixas} casas={0} />
        </Cartao>
        <Cartao
          titulo={`Fila do dia: os 12 pedidos abertos de maior nota (de ${formatarNumero(quadro.estoque.classificaveis)})`}
          ajuda="Os pedidos abertos nesta data, em ordem de prioridade pela nota do AHP. Por onde começar."
        >
          <Tabela
            legenda="Fila do dia"
            colunas={colunasDaFila(nomes)}
            linhas={quadro.fila}
            chave={(_, indice) => String(indice)}
          />
        </Cartao>
      </div>
      <div className={estilos.tresColunas}>
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
              texto: `${formatarNumero(item.atrasados)} · ${formatarPorcentagem((item.atrasados / Math.max(item.abertos, 1)) * 100)}`,
              detalhe: 'pedidos atrasados',
              cor: COR.marinho,
            }))}
            maximo={maximoDeAtraso * 1.5}
            larguraDoRotulo={130}
          />
        </Cartao>
        <Cartao
          titulo="O que mais entrou neste dia"
          ajuda="Categorias e bairros com mais pedidos registrados nesta data."
        >
          {quadro.categoriasDoDia.length === 0 ? (
            <p className={estilos.aviso}>Sem entradas registradas neste dia.</p>
          ) : (
            <ul className={estilos.maisEntradas}>
              {quadro.categoriasDoDia.map((item) => (
                <li key={item.nome}>
                  {nomeDaCategoria(item.nome)} ({formatarNumero(item.n)})
                </li>
              ))}
              {quadro.bairrosDoDia.map((item) => (
                <li key={item.nome}>
                  {nomes.get(item.nome) ?? item.nome} ({formatarNumero(item.n)})
                </li>
              ))}
            </ul>
          )}
        </Cartao>
      </div>
      <section className={estilos.alertas}>
        <h2>Alertas do dia</h2>
        <ul>
          {montarAlertas(quadro, nomes).map((alerta) => (
            <li key={alerta}>{alerta}</li>
          ))}
        </ul>
      </section>
      <p className={estilos.leitura}>
        Como o estoque de cada dia é reconstruído: um pedido conta como aberto da entrada até o
        atendimento, ou até hoje, se continua aberto nos arquivos mais recentes. Pedidos que ficaram
        abertos em arquivos anuais antigos têm destino desconhecido e ficam de fora, então em datas
        antigas o estoque é um piso. Data do quadro: {formatarData(quadro.dia)}.
      </p>
    </>
  )
}
