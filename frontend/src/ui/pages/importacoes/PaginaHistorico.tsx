import { useMemo, useState } from 'react'
import { Link } from 'react-router'

import { useHistorico } from '../../../application/importacoes/useHistorico'
import {
  formatarData,
  formatarDataEHora,
  formatarNumero,
  formatarTamanho,
} from '../../../domain/formatacao'
import {
  ROTULOS_DOS_STATUS,
  descreverFonte,
  type ResumoDaImportacao,
  type StatusDaImportacao,
} from '../../../domain/importacoes'
import { Aviso } from '../../components/Aviso'
import { LinkDeBotao } from '../../components/LinkDeBotao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { useValorAtrasado } from '../../components/useValorAtrasado'
import estilos from './Importacoes.module.css'
import { SeloDeStatus } from './SeloDeStatus'

const ATRASO_DA_BUSCA_EM_MS = 300
const ITENS_POR_PAGINA = 50

function periodoCoberto(importacao: ResumoDaImportacao): string {
  if (!importacao.periodoInicio) return 'sem dado'
  return `${formatarData(importacao.periodoInicio)} a ${formatarData(importacao.periodoFim)}`
}

function totalDeDescartes(importacao: ResumoDaImportacao): number {
  return Object.values(importacao.resultado.descartes).reduce((soma, n) => soma + n, 0)
}

function autoria(importacao: ResumoDaImportacao): string {
  if (importacao.nomeDeQuemImportou) return importacao.nomeDeQuemImportou
  return importacao.cargaInicial ? 'carga inicial' : 'terminal'
}

const COLUNAS: readonly ColunaDaTabela<ResumoDaImportacao>[] = [
  {
    titulo: 'Data e autoria',
    valor: (item) => (
      <>
        {formatarDataEHora(item.criadaEm)}
        <span className={estilos.detalheDaCelula}>{autoria(item)}</span>
      </>
    ),
  },
  {
    titulo: 'Arquivo e fonte',
    valor: (item) => (
      <>
        <Link to={`/painel/importacoes/${item.id}`}>{item.nomeDoArquivo}</Link>
        <span className={estilos.detalheDaCelula}>
          {descreverFonte(item)}, {formatarTamanho(item.tamanhoEmBytes)}
        </span>
      </>
    ),
  },
  { titulo: 'Período', valor: periodoCoberto },
  { titulo: 'Situação', valor: (item) => <SeloDeStatus status={item.status} /> },
  { titulo: 'Novas', numerica: true, valor: (item) => formatarNumero(item.resultado.novas) },
  {
    titulo: 'Atualizadas',
    numerica: true,
    valor: (item) => formatarNumero(item.resultado.atualizadas),
  },
  {
    titulo: 'Descartadas',
    numerica: true,
    valor: (item) => formatarNumero(totalDeDescartes(item)),
  },
]

export function PaginaHistorico() {
  useTituloDaPagina('Histórico de importações')
  const [busca, definirBusca] = useState('')
  const [situacao, definirSituacao] = useState('')
  const [deslocamento, definirDeslocamento] = useState(0)
  const buscaAtrasada = useValorAtrasado(busca, ATRASO_DA_BUSCA_EM_MS)
  const filtro = useMemo(
    () => ({ busca: buscaAtrasada, situacao, deslocamento }),
    [buscaAtrasada, situacao, deslocamento],
  )
  const { pagina, erro } = useHistorico(filtro)
  const total = pagina?.total ?? 0

  return (
    <>
      <div className={estilos.topo}>
        <div>
          <h1 className={estilos.titulo}>Histórico de importações</h1>
          <p className={estilos.subtitulo}>
            Cada arquivo que entrou na base: quando, por quem, o que mudou e o que foi descartado.
          </p>
        </div>
        <LinkDeBotao para="/painel/importacoes/nova" compacto>
          Nova importação
        </LinkDeBotao>
      </div>
      <div className={estilos.filtrosDoHistorico}>
        <label>
          Buscar arquivo ou fonte
          <input
            type="search"
            value={busca}
            onChange={(evento) => {
              definirBusca(evento.target.value)
              definirDeslocamento(0)
            }}
          />
        </label>
        <label>
          Situação
          <select
            value={situacao}
            onChange={(evento) => {
              definirSituacao(evento.target.value)
              definirDeslocamento(0)
            }}
          >
            <option value="">Todas</option>
            {(Object.keys(ROTULOS_DOS_STATUS) as StatusDaImportacao[]).map((status) => (
              <option key={status} value={status}>
                {ROTULOS_DOS_STATUS[status]}
              </option>
            ))}
          </select>
        </label>
      </div>
      {erro ? (
        <Aviso tipo="erro" titulo="Não foi possível carregar o histórico">
          {mensagemDeFalha(erro)}
        </Aviso>
      ) : null}
      {pagina && pagina.itens.length === 0 && (
        <p className={estilos.vazio}>Nenhuma importação com estes filtros.</p>
      )}
      {pagina && pagina.itens.length > 0 && (
        <Tabela
          legenda="Histórico de importações"
          colunas={COLUNAS}
          linhas={pagina.itens}
          chave={(item) => String(item.id)}
        />
      )}
      {total > ITENS_POR_PAGINA && (
        <div className={estilos.paginacao}>
          <button
            type="button"
            disabled={deslocamento === 0}
            onClick={() => definirDeslocamento(deslocamento - ITENS_POR_PAGINA)}
          >
            Anteriores
          </button>
          <span>
            {deslocamento + 1} a {Math.min(deslocamento + ITENS_POR_PAGINA, total)} de {total}
          </span>
          <button
            type="button"
            disabled={deslocamento + ITENS_POR_PAGINA >= total}
            onClick={() => definirDeslocamento(deslocamento + ITENS_POR_PAGINA)}
          >
            Próximas
          </button>
        </div>
      )}
    </>
  )
}
