import { useMemo, useState } from 'react'
import { Link } from 'react-router'

import { useTerritorio } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import {
  formatarNumero,
  formatarNumeroOpcional,
  formatarPeriodo,
  formatarPorcentagem,
} from '../../../../domain/formatacao'
import type {
  BairroDoTerritorio,
  IndicadorDeTerritorio,
  Territorio,
} from '../../../../domain/painel'
import { GraficoDeDispersao } from '../../../charts/GraficoDeDispersao'
import { baixarCsv } from '../../../components/baixarCsv'
import { Botao } from '../../../components/Botao'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Colunas, Secao } from '../../../components/Secao'
import { Tabela, type ColunaDaTabela } from '../../../components/Tabela'
import { LegendaDoMapa } from '../../../map/LegendaDoMapa'
import { MapaCoropletico, type ValorDoBairro } from '../../../map/MapaCoropletico'
import estilos from './PaginaTerritorio.module.css'

const UNIDADE_DO_156 = 'pedidos / mil hab. / ano'
const UNIDADE_DA_DEFESA_CIVIL = 'ações pedidas / mil hab. / ano'
const POPULACAO_MINIMA_TEXTO = 'não calculada (menos de 1.000 moradores)'

function textoDaTaxa(indicador: IndicadorDeTerritorio): string {
  return indicador.taxa === null ? POPULACAO_MINIMA_TEXTO : formatarNumero(indicador.taxa, 1)
}

function valoresDoMapa(
  bairros: readonly BairroDoTerritorio[],
  indicador: (bairro: BairroDoTerritorio) => IndicadorDeTerritorio,
  unidade: string,
): ReadonlyMap<string, ValorDoBairro> {
  return new Map(
    bairros.map((bairro) => {
      const item = indicador(bairro)
      const dica =
        `${bairro.nome} (RPA ${bairro.rpa})\n${textoDaTaxa(item)} ${unidade}\n` +
        `Volume no período: ${formatarNumero(item.volume)}\n` +
        `Em favela: ${formatarPorcentagem(bairro.pctFavela, 1)}`
      return [bairro.nome, { classe: item.classe, emDestaque: bairro.emDestaque, dica }]
    }),
  )
}

function pontosDe(
  bairros: readonly BairroDoTerritorio[],
  indicador: (bairro: BairroDoTerritorio) => IndicadorDeTerritorio,
) {
  return bairros.flatMap((bairro) => {
    const { taxa } = indicador(bairro)
    if (taxa === null) return []
    return [{ x: bairro.pctFavela, y: taxa, nome: bairro.nome, emDestaque: bairro.emDestaque }]
  })
}

const COLUNAS_DA_TABELA: readonly ColunaDaTabela<BairroDoTerritorio>[] = [
  { titulo: 'Bairro', valor: (bairro) => bairro.nome },
  { titulo: 'RPA', valor: (bairro) => bairro.rpa },
  {
    titulo: 'População',
    numerica: true,
    ajuda: 'Moradores do bairro no Censo 2022.',
    valor: (bairro) => formatarNumero(bairro.populacao),
  },
  {
    titulo: '% em favela',
    numerica: true,
    ajuda: 'Parcela da população em favelas e comunidades urbanas (Censo 2022).',
    valor: (bairro) => formatarNumero(bairro.pctFavela, 1),
  },
  {
    titulo: 'Pedidos 156',
    numerica: true,
    valor: (bairro) => formatarNumero(bairro.central156.volume),
  },
  {
    titulo: '156 / mil hab. / ano',
    numerica: true,
    valor: (bairro) => formatarNumeroOpcional(bairro.central156.taxa, 1),
  },
  {
    titulo: 'Ações Def. Civil',
    numerica: true,
    valor: (bairro) => formatarNumero(bairro.defesaCivil.volume),
  },
  {
    titulo: 'Def. Civil / mil hab. / ano',
    numerica: true,
    valor: (bairro) => formatarNumeroOpcional(bairro.defesaCivil.taxa, 1),
  },
]

function exportarTabela(bairros: readonly BairroDoTerritorio[]) {
  baixarCsv(
    'recifeview-territorio.csv',
    [
      'Bairro',
      'RPA',
      'População',
      '% em favela',
      'Pedidos 156',
      'Taxa 156',
      'Ações Defesa Civil',
      'Taxa Defesa Civil',
    ],
    bairros.map((bairro) => [
      bairro.nome,
      bairro.rpa,
      bairro.populacao,
      bairro.pctFavela,
      bairro.central156.volume,
      bairro.central156.taxa ?? '',
      bairro.defesaCivil.volume,
      bairro.defesaCivil.taxa ?? '',
    ]),
  )
}

function DetalheDoBairro({ bairro }: { bairro: BairroDoTerritorio }) {
  return (
    <Secao titulo={`${bairro.nome}, RPA ${bairro.rpa}`}>
      <GradeDeKpis>
        <KpiCard
          rotulo="População"
          valor={formatarNumero(bairro.populacao)}
          contexto={`${formatarPorcentagem(bairro.pctFavela, 1)} em favela`}
          ajuda="Censo 2022 (IBGE)."
        />
        <KpiCard
          rotulo="Pedidos ao 156"
          valor={formatarNumero(bairro.central156.volume)}
          contexto={`${formatarNumeroOpcional(bairro.central156.taxa, 1)} / mil hab. / ano`}
        />
        <KpiCard
          rotulo="Defesa Civil"
          valor={formatarNumero(bairro.defesaCivil.volume)}
          contexto={`${formatarNumeroOpcional(bairro.defesaCivil.taxa, 1)} / mil hab. / ano`}
          ajuda="Ações da Defesa Civil pedidas pelo cidadão (vistoria, lona). A Defesa Civil publica até 2024."
        />
        <KpiCard
          rotulo="Local repetido (156)"
          valor={formatarPorcentagem(bairro.pctReincidencia156, 1)}
          contexto="2021 a 2025"
        />
        <KpiCard
          rotulo="Abertos fora do prazo"
          valor={formatarPorcentagem(bairro.pctAtraso156)}
          contexto={`de ${formatarNumeroOpcional(bairro.abertos156)} abertos`}
        />
      </GradeDeKpis>
      <Link to="/painel/prioridade" className={estilos.link}>
        Ver a posição deste bairro no índice de prioridade
      </Link>
    </Secao>
  )
}

interface ConteudoProps {
  dados: Territorio
  nota: string
}

function ConteudoDoTerritorio({ dados, nota }: ConteudoProps) {
  const { filtros } = useFiltrosGlobais()
  const [clicado, definirClicado] = useState<string | null>(null)
  const unico = filtros.bairros.length === 1 ? filtros.bairros[0] : null
  const escolhido =
    dados.bairros.find((bairro) => bairro.nome === clicado) ??
    dados.bairros.find((bairro) => bairro.bairroOficial === unico)
  const mapa156 = useMemo(
    () => valoresDoMapa(dados.bairros, (bairro) => bairro.central156, UNIDADE_DO_156),
    [dados.bairros],
  )
  const mapaDc = useMemo(
    () => valoresDoMapa(dados.bairros, (bairro) => bairro.defesaCivil, UNIDADE_DA_DEFESA_CIVIL),
    [dados.bairros],
  )
  const ordenados = useMemo(
    () => [...dados.bairros].sort((a, b) => (b.central156.taxa ?? -1) - (a.central156.taxa ?? -1)),
    [dados.bairros],
  )
  const semDefesaCivil = dados.bairros.every((bairro) => bairro.defesaCivil.volume === 0)

  return (
    <>
      <Colunas>
        <Cartao
          titulo="Serviço urbano (156)"
          ajuda="Pedidos ao 156 por mil moradores, por ano. Mais escuro, mais pedidos por habitante. Clique num bairro."
          nota={nota}
        >
          <MapaCoropletico
            rotulo="Pedidos ao 156 por mil habitantes, por bairro do Recife. Os valores estão na tabela por bairro."
            valores={mapa156}
            selecionado={escolhido?.nome}
            aoClicar={definirClicado}
          />
          <LegendaDoMapa titulo={UNIDADE_DO_156} faixas={dados.faixas156} />
        </Cartao>
        <Cartao
          titulo="Emergência (Defesa Civil)"
          ajuda="Ações da Defesa Civil pedidas pelo cidadão por mil moradores, por ano. Clique num bairro."
          nota={
            semDefesaCivil
              ? 'A Defesa Civil publica dados de 2014 a 2024; não há registros no período escolhido.'
              : nota
          }
        >
          <MapaCoropletico
            rotulo="Ações da Defesa Civil por mil habitantes, por bairro do Recife. Os valores estão na tabela por bairro."
            valores={mapaDc}
            selecionado={escolhido?.nome}
            aoClicar={definirClicado}
          />
          <LegendaDoMapa titulo={UNIDADE_DA_DEFESA_CIVIL} faixas={dados.faixasDefesaCivil} />
        </Cartao>
      </Colunas>
      <p className={estilos.leitura}>
        Cores em cinco faixas com o mesmo número de bairros cada, do mais claro (menor taxa) ao mais
        escuro. Bairros hachurados têm menos de 1.000 moradores, e a taxa por habitante distorce. As
        taxas mais altas do 156 estão em bairros centrais e pequenos: o pedido vem de quem circula,
        a população é de quem mora. A emergência se concentra nos morros do Norte e Noroeste e no
        Ibura e na Cohab. Clique num bairro para ver o detalhe.
      </p>
      {escolhido && <DetalheDoBairro bairro={escolhido} />}
      <Secao
        titulo="Mais pedido não quer dizer mais problema"
        ajuda="Cada ponto é um bairro: % da população em favela contra pedidos por habitante."
      >
        <Colunas>
          <Cartao
            titulo="Serviço urbano (156)"
            ajuda="Cada ponto é um bairro. A linha mostra a tendência."
          >
            <GraficoDeDispersao
              pontos={pontosDe(dados.bairros, (bairro) => bairro.central156)}
              tendencia={dados.tendencia156}
              rotuloX="% da população em favela (Censo 2022)"
              rotuloY={UNIDADE_DO_156}
            />
          </Cartao>
          <Cartao
            titulo="Emergência (Defesa Civil)"
            ajuda="Cada ponto é um bairro. A linha mostra a tendência (escala log)."
          >
            <GraficoDeDispersao
              pontos={pontosDe(dados.bairros, (bairro) => bairro.defesaCivil)}
              tendencia={dados.tendenciaDefesaCivil}
              rotuloX="% da população em favela (Censo 2022)"
              rotuloY={`${UNIDADE_DA_DEFESA_CIVIL} (escala log)`}
              escalaLog
            />
          </Cartao>
        </Colunas>
        <p className={estilos.leitura}>
          Serviço urbano: a nuvem é plana. Bairros mais vulneráveis não pedem menos ao 156 por
          habitante. Emergência: a tendência sobe acima de 30% a 40% da população em favela, e
          alguns bairros de morro ficam muito acima dos demais. Por isso o índice de prioridade usa
          a vulnerabilidade como critério próprio, em vez de confiar só no volume de pedidos.
        </p>
      </Secao>
      <details className={estilos.detalhes}>
        <summary>Tabela por bairro (para conferir e exportar)</summary>
        <div className={estilos.tabela}>
          <Botao variante="secundario" compacto onClick={() => exportarTabela(ordenados)}>
            Baixar em CSV
          </Botao>
          <Tabela
            legenda="Indicadores por bairro"
            colunas={COLUNAS_DA_TABELA}
            linhas={ordenados}
            chave={(bairro) => bairro.bairroOficial}
            altura={420}
          />
        </div>
      </details>
    </>
  )
}

export function PaginaTerritorio() {
  const { filtros } = useFiltrosGlobais()
  const consulta = useTerritorio(filtros)
  const periodo = formatarPeriodo(filtros.anoInicio, filtros.anoFim)

  return (
    <>
      <CabecalhoDaTela
        titulo="Território"
        fontes={['156_EMLURB', 'DEFESA_CIVIL']}
        ignorados={[
          'Mapas: RPA e bairro escolhidos ficam em destaque e o resto da cidade continua visível; a categoria vale só para o 156.',
        ]}
        atualizando={consulta.atualizando}
      >
        Há pelo menos dois mapas de prioridade. O pedido de serviço urbano e a demanda de emergência
        apontam para bairros diferentes. A demanda aparece por mil habitantes, porque bairro grande
        pede mais só por ser grande.
      </CabecalhoDaTela>
      <div className={estilos.corpo}>
        <EstadoDaConsulta consulta={consulta}>
          {({ dados, meta }) => (
            <ConteudoDoTerritorio
              dados={dados}
              nota={`Período: ${periodo}. n = ${formatarNumero(meta.n)} nas duas fontes.`}
            />
          )}
        </EstadoDaConsulta>
      </div>
    </>
  )
}
