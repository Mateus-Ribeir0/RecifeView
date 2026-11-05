import { useState } from 'react'

import { usePrazos } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import {
  formatarDias,
  formatarNumero,
  formatarPeriodo,
  formatarPorcentagem,
} from '../../../../domain/formatacao'
import { nomeDaCategoria } from '../../../../domain/nomes'
import type { EstoqueAberto, FaixaDePrazo, Prazos } from '../../../../domain/painel'
import { BarrasEmpilhadas } from '../../../charts/BarrasEmpilhadas'
import { BarrasVerticais } from '../../../charts/BarrasVerticais'
import { COR } from '../../../charts/estilo'
import { GraficoDeLinhas } from '../../../charts/GraficoDeLinhas'
import { PrazoPorCategoriaGrafico } from '../../../charts/PrazoPorCategoriaGrafico'
import { Alternador } from '../../../components/Alternador'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Colunas, Secao } from '../../../components/Secao'
import estilos from './PaginaPrazos.module.css'

const SERIES_DO_PRAZO = [
  { chave: 'mediana', rotulo: 'mediana', cor: COR.medio, forma: 'circulo' as const },
  {
    chave: 'p90',
    rotulo: 'p90 (1 em cada 10 leva mais)',
    cor: COR.marinho,
    forma: 'quadrado' as const,
  },
]
const SEGMENTOS_DO_ESTOQUE = [
  { chave: 'acimaDoPrazo', rotulo: 'passou do prazo típico', cor: COR.marinho },
  { chave: 'noPrazo', rotulo: 'dentro do prazo típico', cor: COR.claro },
]
const CORES_DAS_FAIXAS = [
  'var(--cor-mapa-2)',
  'var(--cor-mapa-2)',
  'var(--cor-mapa-3)',
  'var(--cor-mapa-4)',
  'var(--cor-mapa-5)',
  'var(--cor-mapa-5)',
]

function colunasDasFaixas(faixas: readonly FaixaDePrazo[]) {
  return faixas.map((faixa, indice) => ({
    rotulo: faixa.faixa.replace(/ (\S+)$/, '\n$1'),
    valor: faixa.pct,
    texto: formatarPorcentagem(faixa.pct, 1),
    detalhe: 'dos pedidos atendidos',
    cor: CORES_DAS_FAIXAS[indice],
  }))
}

function linhasDoEstoque(estoque: EstoqueAberto) {
  return estoque.porCategoria.map((item) => ({
    nome: nomeDaCategoria(item.categoria),
    acimaDoPrazo: item.acimaDoPrazo,
    noPrazo: item.abertos - item.acimaDoPrazo,
  }))
}

interface ConteudoProps {
  dados: Prazos
  nota: string
}

function ConteudoDosPrazos({ dados, nota }: ConteudoProps) {
  const { resumo, estoque } = dados
  return (
    <>
      <GradeDeKpis>
        <KpiCard
          rotulo="Metade sai em até"
          valor={formatarDias(resumo.mediana)}
          contexto="mediana"
          ajuda={`Mediana dos dias até a última movimentação, em ${formatarNumero(resumo.pedidos)} pedidos atendidos.`}
        />
        <KpiCard
          rotulo="1 em cada 10 leva mais de"
          valor={formatarDias(resumo.p90)}
          contexto="p90"
          ajuda="Percentil 90: o limite da cauda longa. É o número que mais piorou nos últimos anos."
        />
        <KpiCard
          rotulo="Fechados no mesmo dia"
          valor={formatarPorcentagem(resumo.pctMesmoDia)}
          contexto="prazo de zero dias"
          ajuda="Use a opção acima para tirá-los da conta e ver só os prazos de execução."
        />
        <KpiCard
          rotulo="Mais de 90 dias"
          valor={formatarPorcentagem(resumo.pctAcimaDe90Dias, 1)}
          contexto="dos pedidos atendidos"
          ajuda="Parcela dos atendidos que levou mais de três meses."
        />
      </GradeDeKpis>
      <Secao titulo="Como o prazo se comporta">
        <Colunas>
          <Cartao
            titulo="O prazo piorou na cauda"
            ajuda="Mediana (metade dos pedidos sai antes) e p90 (9 em cada 10 saem antes) dos dias até atender, por ano."
            leitura="A mediana quase não se move; o p90 sobe a partir de 2021. Em 2024 a 2026 a cauda ainda está incompleta: pedidos abertos há muito tempo só entram aqui quando forem atendidos."
            nota={nota}
          >
            <GraficoDeLinhas
              dados={dados.porAno.map((item) => ({ ...item, ano: String(item.ano) }))}
              eixoX="ano"
              series={SERIES_DO_PRAZO}
              rotuloDoEixo="dias até atender"
              formatar={formatarDias}
              altura={300}
            />
          </Cartao>
          <Cartao
            titulo="Em quanto tempo os pedidos são atendidos"
            ajuda="% dos pedidos atendidos em cada faixa de dias."
            leitura="A distribuição é muito assimétrica: a maior parte se resolve em uma semana, e uma fatia pequena leva meses ou anos (obras como escadaria e macrodrenagem)."
            nota={nota}
          >
            <BarrasVerticais
              dados={colunasDasFaixas(dados.faixas)}
              rotuloDoEixo="% dos atendidos"
              altura={320}
            />
          </Cartao>
        </Colunas>
      </Secao>
      <Secao
        titulo="Cada categoria tem o seu prazo"
        ajuda="Mediana e p90 dos dias até atender em cada categoria. Escala log: cada marca é muito maior que a anterior."
      >
        <Cartao
          titulo="Da categoria mais lenta para a mais rápida"
          leitura={`Em cada categoria, o ponto da esquerda é a mediana e o da direita é o p90. Categorias com ${formatarNumero(dados.minimoPorCategoria)} pedidos atendidos ou mais. 10 dias é atraso em iluminação e é rápido em drenagem.`}
          nota={nota}
        >
          <PrazoPorCategoriaGrafico
            dados={dados.porCategoria.map((item) => ({
              ...item,
              nome: nomeDaCategoria(item.categoria),
            }))}
          />
        </Cartao>
      </Secao>
      <Secao
        titulo="A fila de hoje: pedidos abertos que já passaram do prazo típico"
        ajuda="Pedidos ainda abertos e quantos já passaram do p90 da própria categoria."
      >
        {estoque.abertos === 0 ? (
          <p className={estilos.vazio}>
            Sem pedidos abertos para o território ou a categoria escolhidos.
          </p>
        ) : (
          <Colunas proporcao="larga">
            <Cartao
              titulo="As 12 categorias com mais pedidos atrasados"
              leitura="O prazo típico é o da própria categoria. Onde ele é curto (iluminação, limpeza), quase todo pedido ainda aberto já passou dele; em drenagem, cujo p90 chega perto de três anos, quase nenhum passou."
              nota="Fonte: Central 156, dois arquivos anuais mais recentes. O filtro de período não se aplica ao estoque."
            >
              <BarrasEmpilhadas
                dados={linhasDoEstoque(estoque)}
                eixo="nome"
                segmentos={SEGMENTOS_DO_ESTOQUE}
                orientacao="horizontal"
              />
            </Cartao>
            <div className={estilos.pilha}>
              <KpiCard
                rotulo="Pedidos abertos"
                valor={formatarNumero(estoque.abertos)}
                contexto="dois arquivos mais recentes do 156"
              />
              <KpiCard
                rotulo="Passaram do prazo típico"
                valor={formatarPorcentagem(estoque.pctAcimaDoPrazo)}
                contexto={`${formatarNumero(estoque.acimaDoPrazo)} pedidos`}
                ajuda="Idade do pedido na data do retrato maior que o p90 dos atendidos da mesma categoria (2021 a 2025)."
              />
              <p className={estilos.leitura}>
                Só os arquivos mais recentes entram: em arquivos antigos, o pedido aberto pode ter
                só congelado no retrato do ano. Este estoque alimenta o critério Atraso do índice de
                prioridade.
              </p>
            </div>
          </Colunas>
        )}
      </Secao>
    </>
  )
}

export function PaginaPrazos() {
  const { filtros } = useFiltrosGlobais()
  const [semMesmoDia, definirSemMesmoDia] = useState(false)
  const consulta = usePrazos(filtros, semMesmoDia)
  const periodo = formatarPeriodo(filtros.anoInicio, filtros.anoFim)

  return (
    <>
      <CabecalhoDaTela
        titulo="Prazos"
        fontes={['156_EMLURB']}
        ignorados={[
          'Base: pedidos atendidos do 156; os abertos não têm tempo final e entram só no estoque, no fim da tela.',
        ]}
        atualizando={consulta.atualizando}
      >
        Quem demora está demorando mais. A maioria dos pedidos do 156 é atendida em poucos dias, mas
        a cauda longa cresceu. Por isso o prazo aparece em percentis e por categoria: a média
        engana.
      </CabecalhoDaTela>
      <Alternador
        rotulo="Tirar os pedidos fechados no mesmo dia"
        ajuda="Prazo de zero dias costuma ser encerramento administrativo (cancelado, repassado ou fechado na triagem), não execução."
        ligado={semMesmoDia}
        aoMudar={definirSemMesmoDia}
      />
      <EstadoDaConsulta
        consulta={consulta}
        estaVazia={({ dados }) => dados.resumo.pedidos === 0}
        mensagemDeVazio="Sem pedidos atendidos do 156 para estes filtros."
      >
        {({ dados, meta }) => (
          <ConteudoDosPrazos
            dados={dados}
            nota={`Fonte: Central 156. Período: ${periodo}. n = ${formatarNumero(meta.n)}.`}
          />
        )}
      </EstadoDaConsulta>
    </>
  )
}
