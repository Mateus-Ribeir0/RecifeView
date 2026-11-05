import { Link } from 'react-router'

import { useVisaoGeral } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import { temTerritorio, type Filtros } from '../../../../domain/filtros'
import {
  formatarDias,
  formatarNumero,
  formatarPeriodo,
  formatarPorcentagem,
} from '../../../../domain/formatacao'
import { nomeDaFonte, ORDEM_DAS_FONTES, type CodigoDaFonte } from '../../../../domain/fontes'
import type { DemandaPorAno } from '../../../../domain/painel'
import { CORES_DAS_FONTES } from '../../../charts/estilo'
import { GraficoDeLinhas, type SerieDeLinha } from '../../../charts/GraficoDeLinhas'
import type { FormaDoMarcador } from '../../../charts/Marcador'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Secao } from '../../../components/Secao'
import { TELAS_DO_PAINEL } from '../../../conteudo/telasDoPainel'
import estilos from './PaginaInicioDoPainel.module.css'

const FORMAS: Readonly<Record<CodigoDaFonte, FormaDoMarcador>> = {
  '156_EMLURB': 'circulo',
  DEFESA_CIVIL: 'losango',
  OUVIDORIA: 'quadrado',
  SEDEC_CHAMADOS: 'triangulo',
  CAMARA_REQUERIMENTOS: 'cruz',
}
const TELAS_DA_NARRATIVA = [
  '/painel/retorno',
  '/painel/reincidencia',
  '/painel/prazos',
  '/painel/territorio',
  '/painel/prioridade',
]

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

function seriesPresentes(serie: readonly DemandaPorAno[]): SerieDeLinha[] {
  const fontes = new Set(serie.map((ponto) => ponto.fonte))
  return ORDEM_DAS_FONTES.filter((fonte) => fontes.has(fonte)).map((fonte) => ({
    chave: fonte,
    rotulo: nomeDaFonte(fonte),
    cor: CORES_DAS_FONTES[fonte],
    forma: FORMAS[fonte],
  }))
}

function notasDoGrafico(filtros: Filtros): string {
  const notas = ['Clique numa fonte da legenda para destacá-la.']
  if (temTerritorio(filtros)) {
    notas.push(
      'Com filtro de território, a Ouvidoria sai do gráfico: a fonte não publica o bairro.',
    )
  }
  if (filtros.categorias.length) {
    notas.push(
      'Com filtro de categoria, só o 156 e a Câmara ficam: as outras usam outra classificação.',
    )
  }
  notas.push(
    '2025 e 2026 são parciais em algumas fontes; a Defesa Civil mostra só ações pedidas pelo cidadão.',
  )
  return notas.join(' ')
}

export function PaginaInicioDoPainel() {
  const { filtros } = useFiltrosGlobais()
  const consulta = useVisaoGeral(filtros)
  const periodo = formatarPeriodo(filtros.anoInicio, filtros.anoFim)

  return (
    <>
      <CabecalhoDaTela
        titulo="Demandas do cidadão no Recife"
        fontes={ORDEM_DAS_FONTES}
        atualizando={consulta.atualizando}
      >
        Onde, em quais serviços e em que etapa as demandas que chegam à Prefeitura por cinco portas
        diferentes se repetem, demoram ou ficam sem resposta.
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
              />
              <KpiCard
                rotulo="Indicações respondidas"
                valor={formatarPorcentagem(dados.indicacoes.pctRespondidas)}
                contexto={`${formatarPorcentagem(dados.indicacoes.pctEnviadas)} chegam à Prefeitura`}
                ajuda={`Das ${formatarNumero(dados.indicacoes.total)} indicações de vereadores no recorte, a parte que volta com resposta registrada na tramitação da Câmara. Sem resposta registrada não quer dizer não atendido.`}
              />
              <KpiCard
                rotulo="Local repetido (156)"
                valor={formatarPorcentagem(dados.pctLocalRepetido)}
                contexto="156, mesmo local e serviço"
                ajuda="Pedidos do 156 com número no endereço cujo local e serviço aparecem 2 ou mais vezes entre 2015 e 2025."
              />
              <KpiCard
                rotulo="Prazo do 156 (p90)"
                valor={formatarDias(dados.prazo.p90)}
                contexto={`mediana: ${formatarDias(dados.prazo.mediana)}`}
                ajuda="1 em cada 10 pedidos atendidos leva mais que isso. O painel mostra percentis porque a média engana."
              />
            </GradeDeKpis>
            <section className={estilos.mensagem}>
              <h2>A porta de entrada funciona. A perda está depois dela.</h2>
              <p>
                O app Conecta Recife é só cerca de 3% das manifestações da Ouvidoria, e quase toda
                indicação de vereador chega à Prefeitura. O que falha é o caminho de volta: pouca
                coisa retorna com resposta registrada, o mesmo problema volta ao mesmo lugar e uma
                parte dos pedidos fica meses na fila.
              </p>
              <ul className={estilos.atalhos}>
                {TELAS_DO_PAINEL.filter((tela) => TELAS_DA_NARRATIVA.includes(tela.caminho)).map(
                  (tela) => (
                    <li key={tela.caminho}>
                      <Link to={tela.caminho}>{tela.nome}</Link>
                      <p>{tela.mostra}</p>
                    </li>
                  ),
                )}
              </ul>
            </section>
            <Secao
              titulo="Quanto chega por cada porta"
              ajuda="Registros por ano em cada fonte. Clique numa fonte da legenda para destacá-la."
            >
              <Cartao
                titulo="Registros por ano e por fonte"
                nota={`${notasDoGrafico(filtros)} n = ${formatarNumero(meta.n)}.`}
              >
                <GraficoDeLinhas
                  dados={linhasPorAno(dados.serie)}
                  eixoX="ano"
                  series={seriesPresentes(dados.serie)}
                  rotuloDoEixo="registros por ano"
                  altura={400}
                />
              </Cartao>
            </Secao>
          </>
        )}
      </EstadoDaConsulta>
    </>
  )
}
