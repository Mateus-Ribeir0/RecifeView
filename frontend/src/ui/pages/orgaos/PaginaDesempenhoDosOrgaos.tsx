import { Link } from 'react-router'

import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import { useDesempenhoDosOrgaos } from '../../../application/encaminhamentos/useEncaminhamentos'
import {
  ROTULOS_DOS_CANAIS,
  type DesempenhoDoOrgao,
  type DesempenhoDosOrgaos,
} from '../../../domain/encaminhamentos'
import {
  contar,
  formatarDiaEMes,
  formatarDias,
  formatarNumero,
  formatarPorcentagem,
} from '../../../domain/formatacao'
import { nomeDaCategoria } from '../../../domain/nomes'
import { BarrasAgrupadas } from '../../charts/BarrasAgrupadas'
import { BarrasEmpilhadas } from '../../charts/BarrasEmpilhadas'
import { COR } from '../../charts/estilo'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { Cartao } from '../../components/Cartao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { Colunas } from '../../components/Secao'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Orgaos.module.css'

const FONTE =
  'Fonte: encaminhamentos registrados no RecifeView, todos os períodos. No prazo: resolvido até 30 dias depois do envio (Lei 13.460/2017, art. 16).'
const VOLTOU =
  'Voltou a ser pedido: resolvido, e a base ganhou em até 30 dias um registro da mesma fonte, do mesmo local e do mesmo tema. Só vale para fontes com endereço (156 e formulário).'

type CampoSomavel =
  | 'encaminhados'
  | 'abertas'
  | 'vencidas'
  | 'resolvidas'
  | 'resolvidasNoPrazo'
  | 'voltaramASerPedidas'

function somar(orgaos: readonly DesempenhoDoOrgao[], campo: CampoSomavel): number {
  return orgaos.reduce((soma, item) => soma + item[campo], 0)
}

function Indicadores({ desempenho }: { desempenho: DesempenhoDosOrgaos }) {
  const { orgaos } = desempenho
  const resolvidas = somar(orgaos, 'resolvidas')
  const noPrazo = somar(orgaos, 'resolvidasNoPrazo')
  const voltaram = somar(orgaos, 'voltaramASerPedidas')
  return (
    <GradeDeKpis>
      <KpiCard
        rotulo="Encaminhados"
        valor={formatarNumero(somar(orgaos, 'encaminhados'))}
        contexto={`${formatarNumero(somar(orgaos, 'abertas'))} ainda com os órgãos`}
      />
      <KpiCard
        rotulo="Resolvidos no prazo"
        valor={formatarPorcentagem(resolvidas ? (100 * noPrazo) / resolvidas : null)}
        contexto={`${formatarNumero(noPrazo)} de ${formatarNumero(resolvidas)} resolvidos`}
      />
      <KpiCard
        rotulo="Prazo vencido"
        valor={formatarNumero(somar(orgaos, 'vencidas'))}
        contexto="abertos há mais de 30 dias"
        alerta={somar(orgaos, 'vencidas') > 0}
      />
      <KpiCard
        rotulo="Voltaram a ser pedidos"
        valor={formatarNumero(voltaram)}
        contexto={`de ${formatarNumero(resolvidas)} resolvidos, em até 30 dias`}
        ajuda={VOLTOU}
        alerta={voltaram > 0}
      />
    </GradeDeKpis>
  )
}

function SituacaoPorOrgao({ desempenho }: { desempenho: DesempenhoDosOrgaos }) {
  const comEnvio = desempenho.orgaos.filter((item) => item.encaminhados > 0)
  if (comEnvio.length === 0) return <p>Nenhum encaminhamento registrado ainda.</p>
  const dados = comEnvio.map((item) => ({
    orgao: item.nomeDoOrgao,
    resolvidas: item.resolvidas,
    emAtendimento: item.emAtendimento,
    novas: item.novas,
    devolvidas: item.devolvidas,
  }))
  return (
    <BarrasEmpilhadas
      dados={dados}
      eixo="orgao"
      orientacao="horizontal"
      segmentos={[
        { chave: 'resolvidas', rotulo: 'Resolvidas', cor: COR.principal },
        { chave: 'emAtendimento', rotulo: 'Em atendimento', cor: COR.medio },
        { chave: 'novas', rotulo: 'A responder', cor: COR.claro },
        { chave: 'devolvidas', rotulo: 'Devolvidas', cor: COR.contexto },
      ]}
      formatar={(valor) => formatarNumero(valor)}
      larguraDoRotulo={180}
    />
  )
}

function Semanas({ desempenho }: { desempenho: DesempenhoDosOrgaos }) {
  return (
    <BarrasAgrupadas
      dados={desempenho.semanas.map((semana) => ({
        semana: formatarDiaEMes(semana.inicio),
        recebidas: semana.recebidas,
        resolvidas: semana.resolvidas,
      }))}
      eixo="semana"
      series={[
        { chave: 'recebidas', rotulo: 'Encaminhados', cor: COR.contexto },
        { chave: 'resolvidas', rotulo: 'Resolvidos', cor: COR.principal },
      ]}
      altura={240}
    />
  )
}

const COLUNAS: readonly ColunaDaTabela<DesempenhoDoOrgao>[] = [
  { titulo: 'Órgão', valor: (item) => item.nomeDoOrgao },
  { titulo: 'Encaminhados', numerica: true, valor: (item) => formatarNumero(item.encaminhados) },
  { titulo: 'Abertos', numerica: true, valor: (item) => formatarNumero(item.abertas) },
  {
    titulo: 'Prazo vencido',
    numerica: true,
    valor: (item) => (
      <span className={item.vencidas > 0 ? estilos.alerta : undefined}>
        {formatarNumero(item.vencidas)}
      </span>
    ),
  },
  { titulo: 'Resolvidos', numerica: true, valor: (item) => formatarNumero(item.resolvidas) },
  { titulo: 'No prazo', numerica: true, valor: (item) => formatarPorcentagem(item.pctNoPrazo) },
  {
    titulo: 'Até resolver',
    ajuda: 'Mediana de dias entre o envio e a resolução.',
    numerica: true,
    valor: (item) => formatarDias(item.medianaDeDiasAteResolver),
  },
  { titulo: 'Devolvidos', numerica: true, valor: (item) => formatarNumero(item.devolvidas) },
  {
    titulo: 'Voltaram',
    ajuda: VOLTOU,
    numerica: true,
    valor: (item) => formatarNumero(item.voltaramASerPedidas),
  },
  {
    titulo: 'Como recebe',
    valor: (item) =>
      item.acessosAtivos > 0
        ? `${ROTULOS_DOS_CANAIS[item.canal]}, ${contar(item.acessosAtivos, 'acesso ativo', 'acessos ativos')}`
        : `${ROTULOS_DOS_CANAIS[item.canal]}, sem acesso`,
  },
]

function GruposDoMesmoProblema({ desempenho }: { desempenho: DesempenhoDosOrgaos }) {
  const { catalogo } = useCatalogoDoFormulario()
  const nomes = new Map(catalogo?.bairros.map((bairro) => [bairro.chave, bairro.nome]))
  if (desempenho.gruposDoMesmoProblema.length === 0) {
    return <p>Nenhum encaminhamento aberto repete outro agora.</p>
  }
  return (
    <ul className={estilos.grupos}>
      {desempenho.gruposDoMesmoProblema.map((grupo) => (
        <li key={grupo.codigos.join('-')}>
          <strong>
            {nomeDaCategoria(grupo.categoria)} em{' '}
            {nomes.get(grupo.bairroOficial ?? '') ?? grupo.bairroOficial ?? 'bairro não informado'}
          </strong>
          <span>
            {grupo.ids.map((id, indice) => (
              <Link key={id} to={`/painel/encaminhamentos/${id}`}>
                {grupo.codigos[indice]}
              </Link>
            ))}
          </span>
          <span className={estilos.nota}>{grupo.orgaos.join(', ')}</span>
        </li>
      ))}
    </ul>
  )
}

export function PaginaDesempenhoDosOrgaos() {
  useTituloDaPagina('Órgãos')
  const desempenho = useDesempenhoDosOrgaos()
  return (
    <EstadoDaConsulta consulta={consultaDoCarregamento(desempenho)}>
      {(dados) => (
        <div className={estilos.pagina}>
          <CabecalhoDaTela titulo="Desempenho dos órgãos" notas={[FONTE]}>
            Quem recebe, responde e resolve no prazo, e quanto do que foi resolvido voltou a ser
            pedido no mesmo lugar.
          </CabecalhoDaTela>
          <Indicadores desempenho={dados} />
          <Colunas proporcao="larga">
            <Cartao
              titulo="Em que etapa estão os encaminhamentos de cada órgão"
              nota={FONTE}
              leitura="Cada barra soma os encaminhamentos de um órgão, da resolução à devolução."
            >
              <SituacaoPorOrgao desempenho={dados} />
            </Cartao>
            <Cartao
              titulo="Encaminhados e resolvidos por semana"
              nota={`${FONTE} Últimas 12 semanas.`}
            >
              <Semanas desempenho={dados} />
            </Cartao>
          </Colunas>
          <Cartao titulo="Órgão a órgão" nota={`${FONTE} ${VOLTOU}`}>
            <Tabela
              legenda="Desempenho de cada órgão"
              colunas={COLUNAS}
              linhas={dados.orgaos}
              chave={(item) => item.orgao}
            />
          </Cartao>
          <Cartao
            titulo="O mesmo problema em mais de um encaminhamento"
            nota="Abertos agora. Mesma fonte, bairro e tema, menos de 30 dias de diferença e o mesmo local, pela regra do pente fino."
          >
            <GruposDoMesmoProblema desempenho={dados} />
          </Cartao>
        </div>
      )}
    </EstadoDaConsulta>
  )
}
