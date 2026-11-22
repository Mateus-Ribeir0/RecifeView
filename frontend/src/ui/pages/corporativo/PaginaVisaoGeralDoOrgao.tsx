import { Link, useNavigate } from 'react-router'

import { usePainelDoOrgao } from '../../../application/corporativo/useOrgao'
import type { PainelDoOrgao } from '../../../domain/corporativo'
import {
  contar,
  formatarDiaEMes,
  formatarDias,
  formatarNumero,
  formatarPorcentagem,
} from '../../../domain/formatacao'
import { nomeDaCategoria } from '../../../domain/nomes'
import { BarrasAgrupadas } from '../../charts/BarrasAgrupadas'
import { COR } from '../../charts/estilo'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { Cartao } from '../../components/Cartao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { Colunas } from '../../components/Secao'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Corporativo.module.css'
import { MapaDasOcorrencias } from './MapaDasOcorrencias'
import { PrazoRestante } from './PrazoRestante'
import { useNomeDoBairro } from './useNomeDoBairro'

const FONTE_DO_CICLO =
  'Fonte: encaminhamentos registrados no RecifeView. Prazo de 30 dias para resolver ou devolver (Lei 13.460/2017, art. 16).'
const ROTA_DAS_OCORRENCIAS = '/corporativo/ocorrencias'

function Indicadores({ painel }: { painel: PainelDoOrgao }) {
  const { indicadores } = painel
  const mediana = indicadores.medianaDeDiasAteResolver
  return (
    <GradeDeKpis>
      <KpiCard
        rotulo="A responder"
        valor={formatarNumero(indicadores.novas)}
        contexto="ocorrências ainda sem a primeira resposta do órgão"
        para={`${ROTA_DAS_OCORRENCIAS}?aba=novas`}
      />
      <KpiCard
        rotulo="Em atendimento"
        valor={formatarNumero(indicadores.emAtendimento)}
        contexto="o órgão já respondeu e ainda não resolveu"
        para={`${ROTA_DAS_OCORRENCIAS}?aba=em_atendimento`}
      />
      <KpiCard
        rotulo="Prazo vencido"
        valor={formatarNumero(indicadores.vencidas)}
        contexto="abertas há mais de 30 dias"
        alerta={indicadores.vencidas > 0}
        para={`${ROTA_DAS_OCORRENCIAS}?aba=vencidas`}
      />
      <KpiCard
        rotulo="Resolvidas nos últimos 30 dias"
        valor={formatarNumero(indicadores.resolvidasEm30Dias)}
        contexto={
          mediana === null
            ? 'ainda sem resolução registrada'
            : `mediana de ${formatarDias(mediana)} do envio à resolução, ${formatarPorcentagem(indicadores.pctNoPrazo)} no prazo`
        }
        para="/corporativo/resolvidas"
      />
    </GradeDeKpis>
  )
}

function MaisUrgentes({ painel }: { painel: PainelDoOrgao }) {
  const nomeDoBairro = useNomeDoBairro()
  if (painel.maisUrgentes.length === 0) {
    return <p>Nenhuma ocorrência aberta. Quando a gestão encaminhar uma, ela aparece aqui.</p>
  }
  return (
    <ul className={estilos.urgentes}>
      {painel.maisUrgentes.map((item) => (
        <li key={item.id}>
          <Link to={`${ROTA_DAS_OCORRENCIAS}/${item.id}`}>
            {item.codigo}: {nomeDaCategoria(item.categoria)} em {nomeDoBairro(item.bairroOficial)}
          </Link>
          <PrazoRestante item={item} />
        </li>
      ))}
    </ul>
  )
}

function Semanas({ painel }: { painel: PainelDoOrgao }) {
  const dados = painel.semanas.map((semana) => ({
    semana: formatarDiaEMes(semana.inicio),
    recebidas: semana.recebidas,
    resolvidas: semana.resolvidas,
  }))
  return (
    <BarrasAgrupadas
      dados={dados}
      eixo="semana"
      series={[
        { chave: 'recebidas', rotulo: 'Recebidas', cor: COR.contexto },
        { chave: 'resolvidas', rotulo: 'Resolvidas', cor: COR.principal },
      ]}
      altura={240}
    />
  )
}

function MesmoProblema({ painel }: { painel: PainelDoOrgao }) {
  const nomeDoBairro = useNomeDoBairro()
  if (painel.gruposDoMesmoProblema.length === 0) {
    return (
      <p>
        Nenhuma ocorrência aberta repete outra. Quando duas tratarem do mesmo problema, elas
        aparecem juntas aqui e podem receber a mesma resposta.
      </p>
    )
  }
  return (
    <ul className={estilos.urgentes}>
      {painel.gruposDoMesmoProblema.map((grupo) => (
        <li key={grupo.codigos.join('-')}>
          <Link to={`${ROTA_DAS_OCORRENCIAS}/${grupo.ids[0]}`}>
            {nomeDaCategoria(grupo.categoria)} em {nomeDoBairro(grupo.bairroOficial)}
          </Link>
          <span className={estilos.nota}>
            {contar(grupo.ids.length, 'ocorrência', 'ocorrências')}
          </span>
        </li>
      ))}
    </ul>
  )
}

function Painel({ painel }: { painel: PainelDoOrgao }) {
  const navegar = useNavigate()
  const totalAberto = painel.abertasPorBairro.reduce((soma, item) => soma + item.quantidade, 0)
  return (
    <div className={estilos.pagina}>
      <CabecalhoDaTela titulo={`O que chegou para ${painel.nomeDoOrgao}`} notas={[FONTE_DO_CICLO]}>
        Ocorrências que a gestão do Recife encaminhou ao órgão, com o prazo de cada uma e o que já
        foi resolvido.
      </CabecalhoDaTela>
      <Indicadores painel={painel} />
      <Colunas proporcao="larga">
        <Cartao
          titulo="Onde estão as ocorrências abertas"
          nota={`${FONTE_DO_CICLO} n = ${formatarNumero(totalAberto)} abertas.`}
          leitura="Cada bairro tem a cor da quantidade de ocorrências abertas. Clique num bairro para ver as dele."
        >
          {totalAberto === 0 ? (
            <p>Nenhuma ocorrência aberta agora.</p>
          ) : (
            <MapaDasOcorrencias
              rotulo={`Ocorrências abertas de ${painel.nomeDoOrgao} por bairro`}
              contagens={painel.abertasPorBairro}
              unidade={['ocorrência aberta', 'ocorrências abertas']}
              aoClicar={(bairro) =>
                void navegar(
                  `${ROTA_DAS_OCORRENCIAS}?aba=todas&bairro=${encodeURIComponent(bairro)}`,
                )
              }
            />
          )}
        </Cartao>
        <Cartao
          titulo="Vencem primeiro"
          nota="Abertas, da que vence antes para a que vence depois."
        >
          <MaisUrgentes painel={painel} />
        </Cartao>
      </Colunas>
      <Colunas proporcao="larga">
        <Cartao
          titulo="Recebidas e resolvidas, semana a semana"
          nota={`${FONTE_DO_CICLO} Últimas 12 semanas, contadas pela segunda-feira.`}
          leitura="As barras cinza contam o que chegou ao órgão; as azuis, o que ele resolveu na semana."
        >
          <Semanas painel={painel} />
        </Cartao>
        <Cartao
          titulo="Mesmo problema"
          nota="Mesma fonte, bairro e tema, menos de 30 dias de diferença e o mesmo local, pela regra do pente fino."
        >
          <MesmoProblema painel={painel} />
        </Cartao>
      </Colunas>
    </div>
  )
}

export function PaginaVisaoGeralDoOrgao() {
  useTituloDaPagina('Área corporativa')
  const painel = usePainelDoOrgao()
  return (
    <EstadoDaConsulta consulta={consultaDoCarregamento(painel)}>
      {(dados) => <Painel painel={dados} />}
    </EstadoDaConsulta>
  )
}
