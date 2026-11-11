import { useState } from 'react'
import { Link } from 'react-router'

import {
  useOrgaos,
  useQuadroDeEncaminhamentos,
} from '../../../application/encaminhamentos/useEncaminhamentos'
import {
  FILTRO_INICIAL_DE_ENCAMINHAMENTOS,
  ROTULOS_DAS_SITUACOES,
  ROTULOS_DOS_CANAIS,
  SITUACOES_DO_FILTRO,
  type Encaminhamento,
  type FiltroDeEncaminhamentos,
  type Orgao,
  type ResumoDosEncaminhamentos,
  type SituacaoDoEncaminhamento,
} from '../../../domain/encaminhamentos'
import {
  formatarData,
  formatarDataEHora,
  formatarDias,
  formatarNumero,
} from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Botao } from '../../components/Botao'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import estilos from './Encaminhamentos.module.css'
import { SeloDoEncaminhamento } from './SeloDoEncaminhamento'

const ITENS_POR_PAGINA = 50
const NOTA_DA_TELA =
  'Fonte: encaminhamentos registrados no RecifeView. Prazo de 30 dias para resolver ou devolver, como na Lei 13.460/2017, art. 16.'

function Indicadores({ resumo }: { resumo: ResumoDosEncaminhamentos }) {
  const resolvidos = resumo.porSituacao.resolvido ?? 0
  const precisamDeAcao = (resumo.porSituacao.devolvido ?? 0) + (resumo.porSituacao.falhou ?? 0)
  return (
    <GradeDeKpis>
      <KpiCard
        rotulo="Com o órgão"
        valor={formatarNumero(resumo.abertos)}
        contexto={`de ${formatarNumero(resumo.total)} encaminhamentos`}
      />
      <KpiCard
        rotulo="Prazo vencido"
        valor={formatarNumero(resumo.atrasados)}
        contexto="mais de 30 dias sem resolver nem devolver"
        alerta={resumo.atrasados > 0}
      />
      <KpiCard
        rotulo="Resolvidos"
        valor={formatarNumero(resolvidos)}
        contexto={
          resumo.medianaDeDiasAteResolver === null
            ? 'ainda sem resolução registrada'
            : `mediana de ${formatarDias(resumo.medianaDeDiasAteResolver)} até resolver`
        }
      />
      <KpiCard
        rotulo="Precisam de outro passo"
        valor={formatarNumero(precisamDeAcao)}
        contexto="devolvidos pelo órgão ou com falha no envio"
        alerta={precisamDeAcao > 0}
      />
    </GradeDeKpis>
  )
}

const COLUNAS: readonly ColunaDaTabela<Encaminhamento>[] = [
  {
    titulo: 'Código',
    valor: (item) => <Link to={`/painel/encaminhamentos/${item.id}`}>{item.codigo}</Link>,
  },
  { titulo: 'Órgão', valor: (item) => item.nomeDoOrgao },
  {
    titulo: 'Ocorrência',
    valor: (item) =>
      `${nomeDaFonte(item.ocorrencia.fonte)}: ${nomeDaCategoria(item.ocorrencia.categoria)}`,
  },
  { titulo: 'Encaminhado em', valor: (item) => formatarDataEHora(item.criadoEm) },
  { titulo: 'Prazo', valor: (item) => formatarData(item.prazoDeResposta) },
  {
    titulo: 'Situação',
    valor: (item) => <SeloDoEncaminhamento situacao={item.situacao} atrasado={item.atrasado} />,
  },
  {
    titulo: 'Como saiu',
    ajuda: 'Quem encaminhou e por qual canal a mensagem foi.',
    valor: (item) =>
      `${item.automatico ? 'Automático' : 'Pela gestão'}, ${ROTULOS_DOS_CANAIS[item.canal]}`,
  },
]

interface FiltrosProps {
  filtro: FiltroDeEncaminhamentos
  aoMudar: (filtro: FiltroDeEncaminhamentos) => void
}

function FiltrosDaLista({ filtro, aoMudar }: FiltrosProps) {
  const { dados: orgaos } = useOrgaos()
  const mudar = (parcial: Partial<FiltroDeEncaminhamentos>) =>
    aoMudar({ ...filtro, ...parcial, deslocamento: 0 })
  return (
    <div className={estilos.filtros}>
      <label>
        Situação
        <select
          value={filtro.situacao ?? ''}
          onChange={(evento) =>
            mudar({ situacao: (evento.target.value || null) as SituacaoDoEncaminhamento | null })
          }
        >
          <option value="">Todas</option>
          {SITUACOES_DO_FILTRO.map((situacao) => (
            <option key={situacao} value={situacao}>
              {ROTULOS_DAS_SITUACOES[situacao]}
            </option>
          ))}
        </select>
      </label>
      <label>
        Órgão
        <select
          value={filtro.orgao ?? ''}
          onChange={(evento) => mudar({ orgao: (evento.target.value || null) as Orgao | null })}
        >
          <option value="">Todos</option>
          {orgaos?.map((item) => (
            <option key={item.orgao} value={item.orgao}>
              {item.nome}
            </option>
          ))}
        </select>
      </label>
      <label className={estilos.marcacao}>
        <input
          type="checkbox"
          checked={filtro.soAtrasados}
          onChange={(evento) => mudar({ soAtrasados: evento.target.checked })}
        />
        Só com prazo vencido
      </label>
    </div>
  )
}

interface PaginacaoProps {
  total: number
  filtro: FiltroDeEncaminhamentos
  aoMudar: (filtro: FiltroDeEncaminhamentos) => void
}

function Paginacao({ total, filtro, aoMudar }: PaginacaoProps) {
  if (total <= ITENS_POR_PAGINA) return null
  const inicio = filtro.deslocamento + 1
  const fim = Math.min(filtro.deslocamento + ITENS_POR_PAGINA, total)
  return (
    <div className={estilos.paginacao}>
      <Botao
        variante="secundario"
        compacto
        disabled={filtro.deslocamento === 0}
        onClick={() => aoMudar({ ...filtro, deslocamento: filtro.deslocamento - ITENS_POR_PAGINA })}
      >
        Anteriores
      </Botao>
      <span>
        {formatarNumero(inicio)} a {formatarNumero(fim)} de {formatarNumero(total)}
      </span>
      <Botao
        variante="secundario"
        compacto
        disabled={fim >= total}
        onClick={() => aoMudar({ ...filtro, deslocamento: filtro.deslocamento + ITENS_POR_PAGINA })}
      >
        Próximos
      </Botao>
    </div>
  )
}

export function PaginaEncaminhamentos() {
  const [filtro, definirFiltro] = useState(FILTRO_INICIAL_DE_ENCAMINHAMENTOS)
  const quadro = useQuadroDeEncaminhamentos(filtro)

  return (
    <>
      <CabecalhoDaTela titulo="Encaminhamentos">
        Para qual órgão cada ocorrência priorizada foi, se ele já respondeu e o que ainda espera um
        passo da gestão.
      </CabecalhoDaTela>
      <EstadoDaConsulta consulta={consultaDoCarregamento(quadro)}>
        {(dados) => (
          <>
            <Indicadores resumo={dados.resumo} />
            <FiltrosDaLista filtro={filtro} aoMudar={definirFiltro} />
            {dados.itens.length === 0 ? (
              <p className={estilos.nota}>
                Nenhum encaminhamento neste recorte. As ocorrências saem pela fila da tela{' '}
                <Link to="/painel/prioridade">Prioridade</Link> ou pelo envio automático do
                terminal.
              </p>
            ) : (
              <Tabela
                legenda="Encaminhamentos, do mais novo ao mais antigo"
                colunas={COLUNAS}
                linhas={dados.itens}
                chave={(item) => String(item.id)}
              />
            )}
            <Paginacao total={dados.total} filtro={filtro} aoMudar={definirFiltro} />
            <p className={estilos.nota}>{NOTA_DA_TELA}</p>
          </>
        )}
      </EstadoDaConsulta>
    </>
  )
}
