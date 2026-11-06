import { useState } from 'react'

import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { useRegistrosImportados } from '../../../application/importacoes/useHistorico'
import { formatarData, formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import {
  descreverDecisoes,
  type DetalheDaImportacao,
  type RegistroImportado,
} from '../../../domain/importacoes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { LinkDeBotao } from '../../components/LinkDeBotao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import estilos from './Importacoes.module.css'
import { ResumoEmNumeros } from './ResumoEmNumeros'

const REGISTROS_POR_PAGINA = 50

const COLUNAS: readonly ColunaDaTabela<RegistroImportado>[] = [
  { titulo: 'Fonte', valor: (item) => nomeDaFonte(item.fonte) },
  { titulo: 'Abertura', valor: (item) => formatarData(item.dataAbertura) },
  { titulo: 'Último movimento', valor: (item) => formatarData(item.dataUltMovimento) },
  { titulo: 'Categoria', valor: (item) => nomeDaCategoria(item.categoria) },
  { titulo: 'Serviço', valor: (item) => nomeDaCategoria(item.servico) },
  { titulo: 'Bairro', valor: (item) => nomeDaCategoria(item.bairroOficial) },
  { titulo: 'RPA', valor: (item) => item.rpa ?? 'sem dado' },
  { titulo: 'Situação', valor: (item) => nomeDaCategoria(item.situacao) },
]

function RegistrosTratados({ id }: { id: number }) {
  const [deslocamento, definirDeslocamento] = useState(0)
  const pagina = useRegistrosImportados(id, deslocamento)
  if (!pagina) return <p className={estilos.subtitulo}>Carregando registros...</p>
  if (pagina.itens.length === 0) {
    return <p className={estilos.subtitulo}>Nenhum registro desta importação está na base.</p>
  }
  return (
    <>
      <Tabela
        legenda="Registros tratados desta importação"
        colunas={COLUNAS}
        linhas={pagina.itens}
        chave={(_, indice) => String(deslocamento + indice)}
        altura={420}
      />
      <div className={estilos.paginacao}>
        <button
          type="button"
          disabled={deslocamento === 0}
          onClick={() => definirDeslocamento(deslocamento - REGISTROS_POR_PAGINA)}
        >
          Anteriores
        </button>
        <span>
          {formatarNumero(deslocamento + 1)} a{' '}
          {formatarNumero(Math.min(deslocamento + REGISTROS_POR_PAGINA, pagina.total))} de{' '}
          {formatarNumero(pagina.total)}
        </span>
        <button
          type="button"
          disabled={deslocamento + REGISTROS_POR_PAGINA >= pagina.total}
          onClick={() => definirDeslocamento(deslocamento + REGISTROS_POR_PAGINA)}
        >
          Próximos
        </button>
      </div>
    </>
  )
}

interface Propriedades {
  importacao: DetalheDaImportacao
  aoMudar: () => void
}

export function RelatorioDaImportacao({ importacao, aoMudar }: Propriedades) {
  const servico = useServicoDeImportacoes()
  const [confirmando, definirConfirmando] = useState(false)
  const [erro, definirErro] = useState<unknown>(null)
  const { resultado, status } = importacao
  const decisoes = descreverDecisoes(importacao.decisoes)
  const descartadas = Object.values(resultado.descartes).reduce((soma, n) => soma + n, 0)

  async function desfazer() {
    definirErro(null)
    try {
      await servico.desfazer(importacao.id)
      aoMudar()
    } catch (falha) {
      definirErro(falha)
      definirConfirmando(false)
    }
  }

  if (status === 'FALHOU' || status === 'CANCELADA') {
    return (
      <section className={estilos.passo}>
        {status === 'FALHOU' ? (
          <Aviso tipo="erro" titulo="A importação não terminou">
            {importacao.mensagemDeErro ?? 'Tente enviar o arquivo de novo.'}
          </Aviso>
        ) : (
          <Aviso tipo="info" titulo="Importação cancelada">
            Nada foi gravado e o arquivo foi removido.
          </Aviso>
        )}
        <div className={estilos.acoes}>
          <LinkDeBotao para="/painel/importacoes/nova" compacto>
            Nova importação
          </LinkDeBotao>
        </div>
      </section>
    )
  }

  return (
    <section className={estilos.passo} aria-labelledby="titulo-do-relatorio">
      <h2 id="titulo-do-relatorio">Relatório da importação</h2>
      {status === 'CONCLUIDA' && (
        <Aviso tipo="sucesso" titulo="O painel já está com estes dados">
          Concluída em {formatarDataEHora(importacao.concluidaEm)}.
        </Aviso>
      )}
      {status === 'DESFEITA' && (
        <Aviso tipo="info" titulo="Importação desfeita">
          Desfeita em {formatarDataEHora(importacao.desfeitaEm)}. A base voltou ao estado anterior.
        </Aviso>
      )}
      <ResumoEmNumeros
        numeros={[
          { rotulo: 'Linhas lidas', valor: resultado.lidas },
          { rotulo: 'Novas', valor: resultado.novas },
          { rotulo: 'Atualizadas', valor: resultado.atualizadas },
          {
            rotulo: 'Relatos retirados',
            valor: resultado.retiradas,
            contexto: 'cobertos pelo registro oficial',
          },
          { rotulo: 'Idênticas', valor: resultado.iguais },
          { rotulo: 'Ignoradas', valor: resultado.ignoradas },
          { rotulo: 'Descartadas', valor: descartadas },
        ]}
        descartes={resultado.descartes}
        correcoes={resultado.correcoes}
      />
      <dl className={estilos.ficha}>
        <div>
          <dt>Período coberto</dt>
          <dd>
            {formatarData(importacao.periodoInicio)} a {formatarData(importacao.periodoFim)}
          </dd>
        </div>
        <div>
          <dt>Data do retrato</dt>
          <dd>{formatarData(importacao.dataDoRetrato)}</dd>
        </div>
        <div>
          <dt>Quem importou</dt>
          <dd>{importacao.nomeDeQuemImportou ?? 'pelo terminal'}</dd>
        </div>
        <div>
          <dt>Arquivo original</dt>
          <dd>
            {importacao.arquivoGuardado
              ? 'guardado na camada bruta'
              : 'apagado depois da carga (tinha coluna sensível)'}
          </dd>
        </div>
      </dl>
      {decisoes.length > 0 && (
        <div className={estilos.listasDoResumo}>
          <div>
            <h3>Decisões tomadas</h3>
            <ul>
              {decisoes.map((decisao) => (
                <li key={decisao}>{decisao}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
      {erro ? (
        <Aviso tipo="erro" titulo="Não foi possível desfazer">
          {mensagemDeFalha(erro)}
        </Aviso>
      ) : null}
      {importacao.podeDesfazer && (
        <div className={estilos.acoes}>
          {confirmando ? (
            <>
              <p className={estilos.subtitulo}>
                Isso tira as linhas novas, restaura as atualizadas e recalcula o painel. Confirma?
              </p>
              <Botao compacto onClick={() => void desfazer()}>
                Sim, desfazer
              </Botao>
              <Botao variante="secundario" compacto onClick={() => definirConfirmando(false)}>
                Manter
              </Botao>
            </>
          ) : (
            <Botao variante="secundario" compacto onClick={() => definirConfirmando(true)}>
              Desfazer esta importação
            </Botao>
          )}
        </div>
      )}
      {status === 'CONCLUIDA' && (
        <>
          <h3 className={estilos.subtituloDaSecao}>Registros tratados</h3>
          <p className={estilos.subtitulo}>
            O que está na base vindo deste arquivo. Endereço, pseudônimo e texto livre nunca
            aparecem.
          </p>
          <RegistrosTratados id={importacao.id} />
        </>
      )}
    </section>
  )
}
