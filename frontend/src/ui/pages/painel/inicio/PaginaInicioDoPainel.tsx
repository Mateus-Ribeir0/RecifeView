import { useMemo } from 'react'
import { Link } from 'react-router'

import {
  usePrazos,
  useTerritorio,
  useVisaoGeral,
} from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import { temTerritorio, type Filtros } from '../../../../domain/filtros'
import {
  formatarDias,
  formatarNumero,
  formatarPeriodo,
  formatarPorcentagem,
} from '../../../../domain/formatacao'
import { nomeDaFonte, ORDEM_DAS_FONTES, type CodigoDaFonte } from '../../../../domain/fontes'
import type { BairroDoTerritorio, DemandaPorAno, VisaoGeral } from '../../../../domain/painel'
import { BarraDeComposicao } from '../../../charts/BarraDeComposicao'
import { CORES_DAS_FONTES } from '../../../charts/estilo'
import { Funil } from '../../../charts/Funil'
import { GraficoDeLinhas, type SerieDeLinha } from '../../../charts/GraficoDeLinhas'
import type { FormaDoMarcador } from '../../../charts/Marcador'
import { Sparkline } from '../../../charts/Sparkline'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Medidor } from '../../../components/Medidor'
import { Colunas, Secao } from '../../../components/Secao'
import { LegendaDoMapa } from '../../../map/LegendaDoMapa'
import { MapaCoropletico, type ValorDoBairro } from '../../../map/MapaCoropletico'

const FORMAS: Readonly<Record<CodigoDaFonte, FormaDoMarcador>> = {
  '156_EMLURB': 'circulo',
  DEFESA_CIVIL: 'losango',
  OUVIDORIA: 'quadrado',
  SEDEC_CHAMADOS: 'triangulo',
  CAMARA_REQUERIMENTOS: 'cruz',
}
const UNIDADE_DO_MAPA = 'pedidos ao 156 / mil hab. / ano'
const ALTURA_DO_GRAFICO = 320
const ALTURA_DO_MAPA = 300

function linhasPorAno(serie: readonly DemandaPorAno[]) {
  const anos = [...new Set(serie.map((ponto) => ponto.ano))].sort((a, b) => a - b)
  return anos.map((ano) => {
    const linha: Record<string, number | string | null> = { ano: String(ano) }
    serie
      .filter((ponto) => ponto.ano === ano)
      .forEach((ponto) => {
        linha[ponto.fonte] = ponto.n
      })
    return linha
  })
}

function totaisPorAno(serie: readonly DemandaPorAno[]): number[] {
  const totais = new Map<number, number>()
  serie.forEach(({ ano, n }) => totais.set(ano, (totais.get(ano) ?? 0) + n))
  return [...totais.entries()].sort(([a], [b]) => a - b).map(([, total]) => total)
}

function seriesPresentes(serie: readonly DemandaPorAno[]): SerieDeLinha[] {
  const fontes = new Set(serie.map((ponto) => ponto.fonte))
  return ORDEM_DAS_FONTES.filter((fonte) => fontes.has(fonte)).map((fonte) => ({
    chave: fonte,
    rotulo: nomeDaFonte(fonte),
    cor: CORES_DAS_FONTES[fonte],
    forma: FORMAS[fonte],
  }))
}

function partesPorFonte(serie: readonly DemandaPorAno[]) {
  return ORDEM_DAS_FONTES.map((fonte) => ({
    chave: fonte,
    rotulo: nomeDaFonte(fonte),
    cor: CORES_DAS_FONTES[fonte],
    textoEscuro: fonte === 'CAMARA_REQUERIMENTOS',
    valor: serie.filter((ponto) => ponto.fonte === fonte).reduce((soma, { n }) => soma + n, 0),
  }))
    .filter((parte) => parte.valor > 0)
    .sort((a, b) => b.valor - a.valor)
}

function notasDaTela(filtros: Filtros): string[] {
  const notas = [
    '2025 e 2026 são parciais em algumas fontes. Na Defesa Civil entram só as ações pedidas pelo cidadão.',
  ]
  if (temTerritorio(filtros)) {
    notas.push('Com filtro de território, a Ouvidoria sai: a fonte não publica o bairro.')
  }
  if (filtros.categorias.length) {
    notas.push('Com filtro de categoria, só o 156 e a Câmara ficam: as outras usam outra lista.')
  }
  return notas
}

function valoresDoMapa(bairros: readonly BairroDoTerritorio[]) {
  return new Map<string, ValorDoBairro>(
    bairros.map((bairro) => [
      bairro.nome,
      {
        classe: bairro.central156.classe,
        emDestaque: bairro.emDestaque,
        dica: `${bairro.nome}\n${formatarNumero(bairro.central156.taxa ?? 0, 1)} ${UNIDADE_DO_MAPA}`,
      },
    ]),
  )
}

function MapaDaDemanda() {
  const { filtros } = useFiltrosGlobais()
  const consulta = useTerritorio(filtros)
  const bairros = consulta.dados?.dados.bairros
  const valores = useMemo(() => valoresDoMapa(bairros ?? []), [bairros])

  return (
    <Cartao
      titulo="Onde a demanda se concentra"
      ajuda="Pedidos ao 156 por mil moradores, por ano. Quanto mais escuro, mais pedidos por habitante."
      acao={<Link to="/painel/territorio">Ver território</Link>}
    >
      <EstadoDaConsulta consulta={consulta}>
        {({ dados }) => (
          <>
            <MapaCoropletico
              rotulo="Pedidos ao 156 por mil habitantes, por bairro do Recife. A tabela está na tela Território."
              valores={valores}
              altura={ALTURA_DO_MAPA}
            />
            <LegendaDoMapa titulo={UNIDADE_DO_MAPA} faixas={dados.faixas156} />
          </>
        )}
      </EstadoDaConsulta>
    </Cartao>
  )
}

function etapasDoFunil({ indicacoes }: VisaoGeral) {
  return [
    { chave: 'apresentadas', rotulo: 'Apresentadas na Câmara', valor: indicacoes.total },
    { chave: 'enviadas', rotulo: 'Chegam à Prefeitura', valor: indicacoes.enviadas },
    {
      chave: 'respondidas',
      rotulo: 'Voltam com resposta registrada',
      valor: indicacoes.respondidas,
    },
  ]
}

export function PaginaInicioDoPainel() {
  const { filtros } = useFiltrosGlobais()
  const consulta = useVisaoGeral(filtros)
  const prazos = usePrazos(filtros, false)
  const periodo = formatarPeriodo(filtros.anoInicio, filtros.anoFim)
  const seriePorAno = prazos.dados?.dados.porAno.map((item) => item.p90 ?? 0) ?? []

  return (
    <>
      <CabecalhoDaTela
        titulo="Demandas do cidadão no Recife"
        fontes={ORDEM_DAS_FONTES}
        notas={notasDaTela(filtros)}
        atualizando={consulta.atualizando}
      >
        Onde, em quais serviços e em que etapa as demandas se repetem, demoram ou ficam sem
        resposta.
      </CabecalhoDaTela>
      <EstadoDaConsulta consulta={consulta}>
        {({ dados, meta }) => (
          <>
            <GradeDeKpis>
              <KpiCard
                rotulo="Demandas registradas"
                valor={formatarNumero(dados.demandas)}
                contexto={`cinco fontes, ${periodo}`}
                ajuda="Pedidos, manifestações, chamados e indicações das cinco fontes no recorte. Na Defesa Civil, só as ações pedidas pelo cidadão."
                visual={
                  <Sparkline
                    valores={totaisPorAno(dados.serie)}
                    rotulo="Total de registros por ano"
                  />
                }
              />
              <KpiCard
                rotulo="Indicações com resposta"
                valor={formatarPorcentagem(dados.indicacoes.pctRespondidas)}
                contexto={`${formatarPorcentagem(dados.indicacoes.pctEnviadas)} chegam à Prefeitura`}
                ajuda={`Das ${formatarNumero(dados.indicacoes.total)} indicações de vereadores no recorte, a parte que volta com resposta registrada. Sem resposta registrada não quer dizer não atendido.`}
                para="/painel/retorno"
                visual={
                  <Medidor
                    porcentagem={dados.indicacoes.pctRespondidas ?? 0}
                    rotulo="Parte das indicações com resposta registrada"
                  />
                }
              />
              <KpiCard
                rotulo="Pedidos em local repetido"
                valor={formatarPorcentagem(dados.pctLocalRepetido)}
                contexto="156, mesmo local e serviço"
                ajuda="Pedidos do 156 com número no endereço cujo local e serviço aparecem 2 ou mais vezes entre 2015 e 2025."
                para="/painel/reincidencia"
                visual={
                  <Medidor
                    porcentagem={dados.pctLocalRepetido ?? 0}
                    rotulo="Parte dos pedidos em local repetido"
                  />
                }
              />
              <KpiCard
                rotulo="Prazo do 156 (p90)"
                valor={formatarDias(dados.prazo.p90)}
                contexto={`mediana: ${formatarDias(dados.prazo.mediana)}`}
                ajuda="1 em cada 10 pedidos atendidos leva mais que isso. O painel mostra percentis porque a média engana."
                para="/painel/prazos"
                visual={<Sparkline valores={seriePorAno} rotulo="Prazo p90 do 156 por ano" />}
              />
            </GradeDeKpis>
            <Colunas proporcao="larga">
              <Cartao
                titulo="Quanto chega por cada porta"
                ajuda="Registros por ano em cada fonte. Clique numa fonte da legenda para destacá-la."
                nota={`Fonte: as cinco bases. Período: ${periodo}. n = ${formatarNumero(meta.n)}.`}
              >
                <GraficoDeLinhas
                  dados={linhasPorAno(dados.serie)}
                  eixoX="ano"
                  series={seriesPresentes(dados.serie)}
                  rotuloDoEixo="registros por ano"
                  altura={ALTURA_DO_GRAFICO}
                />
              </Cartao>
              <MapaDaDemanda />
            </Colunas>
            <Secao titulo="A porta de entrada funciona. A perda está depois dela.">
              <Colunas>
                <Cartao
                  titulo="O caminho de uma indicação de vereador"
                  ajuda="A Câmara é a única fonte pública que mostra o caminho inteiro, do pedido até a resposta."
                  nota={`Fonte: Câmara Municipal (SAGL). Período: ${periodo}.`}
                >
                  <Funil etapas={etapasDoFunil(dados)} />
                </Cartao>
                <Cartao
                  titulo="De onde vêm as demandas"
                  ajuda="Parte de cada fonte no total do recorte."
                  nota={`Período: ${periodo}. n = ${formatarNumero(meta.n)}.`}
                >
                  <BarraDeComposicao partes={partesPorFonte(dados.serie)} unidade="registros" />
                </Cartao>
              </Colunas>
            </Secao>
          </>
        )}
      </EstadoDaConsulta>
    </>
  )
}
