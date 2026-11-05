import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { useImportacao } from '../../../application/importacoes/useImportacao'
import { formatarDataEHora, formatarTamanho } from '../../../domain/formatacao'
import {
  estaEmProcessamento,
  ROTULOS_DOS_STATUS,
  type DetalheDaImportacao,
  type StatusDaImportacao,
  descreverFonte,
} from '../../../domain/importacoes'
import { Aviso } from '../../components/Aviso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { EtapasDaImportacao } from './EtapasDaImportacao'
import estilos from './Importacoes.module.css'
import { PassoColunas } from './PassoColunas'
import { PassoPendencias } from './PassoPendencias'
import { PassoRevisao } from './PassoRevisao'
import { RelatorioDaImportacao } from './RelatorioDaImportacao'
import { SeloDeStatus } from './SeloDeStatus'

const ETAPA_POR_STATUS: Readonly<Record<StatusDaImportacao, number>> = {
  ANALISANDO: 1,
  AGUARDANDO_COLUNAS: 2,
  VALIDANDO: 3,
  AGUARDANDO_DECISOES: 3,
  PRONTA: 4,
  CARREGANDO: 5,
  ATUALIZANDO_PAINEL: 5,
  CONCLUIDA: 6,
  FALHOU: 6,
  CANCELADA: 6,
  DESFAZENDO: 6,
  DESFEITA: 6,
}

function ProgressoDaImportacao({ importacao }: { importacao: DetalheDaImportacao }) {
  const temPercentual = importacao.progresso > 0
  return (
    <section className={estilos.passo} role="status">
      <h2>{ROTULOS_DOS_STATUS[importacao.status]}...</h2>
      <progress
        className={estilos.barra}
        aria-label={ROTULOS_DOS_STATUS[importacao.status]}
        value={temPercentual ? importacao.progresso : undefined}
        max={100}
      />
      <p className={estilos.subtitulo}>
        Pode sair desta tela: o trabalho continua e o resultado fica no histórico. O painel segue no
        ar durante a atualização.
      </p>
    </section>
  )
}

interface PassoProps {
  importacao: DetalheDaImportacao
  aoMudar: () => void
  aoCancelar: () => void
}

function PassoAtual({ importacao, aoMudar, aoCancelar }: PassoProps) {
  if (estaEmProcessamento(importacao.status)) {
    return <ProgressoDaImportacao importacao={importacao} />
  }
  if (importacao.status === 'AGUARDANDO_COLUNAS') {
    return <PassoColunas importacao={importacao} aoConcluir={aoMudar} aoCancelar={aoCancelar} />
  }
  if (importacao.status === 'AGUARDANDO_DECISOES') {
    return (
      <PassoPendencias
        key={JSON.stringify(importacao.decisoes)}
        importacao={importacao}
        aoConcluir={aoMudar}
        aoCancelar={aoCancelar}
      />
    )
  }
  if (importacao.status === 'PRONTA') {
    return <PassoRevisao importacao={importacao} aoConcluir={aoMudar} aoCancelar={aoCancelar} />
  }
  return <RelatorioDaImportacao importacao={importacao} aoMudar={aoMudar} />
}

export function PaginaImportacao() {
  const { id } = useParams()
  const numero = Number(id)
  const servico = useServicoDeImportacoes()
  const { importacao, erro, recarregar } = useImportacao(numero)
  const [falhaAoCancelar, definirFalhaAoCancelar] = useState<unknown>(null)
  useTituloDaPagina(importacao ? importacao.nomeDoArquivo : 'Importação')

  async function cancelar() {
    try {
      await servico.cancelar(numero)
      recarregar()
    } catch (falha) {
      definirFalhaAoCancelar(falha)
    }
  }

  if (erro && !importacao) {
    return (
      <Aviso tipo="erro" titulo="Não foi possível abrir esta importação">
        {mensagemDeFalha(erro)}
      </Aviso>
    )
  }
  if (!importacao) return <p className={estilos.subtitulo}>Carregando...</p>

  return (
    <>
      <p className={estilos.voltar}>
        <Link to="/painel/importacoes">Histórico de importações</Link>
      </p>
      <div className={estilos.topo}>
        <div>
          <h1 className={estilos.titulo}>{importacao.nomeDoArquivo}</h1>
          <p className={estilos.subtitulo}>
            {descreverFonte(importacao)} · {formatarTamanho(importacao.tamanhoEmBytes)} · enviado em{' '}
            {formatarDataEHora(importacao.criadaEm)}
          </p>
        </div>
        <SeloDeStatus status={importacao.status} />
      </div>
      <EtapasDaImportacao atual={ETAPA_POR_STATUS[importacao.status]} />
      {falhaAoCancelar ? (
        <Aviso tipo="erro" titulo="Não foi possível cancelar">
          {mensagemDeFalha(falhaAoCancelar)}
        </Aviso>
      ) : null}
      <PassoAtual importacao={importacao} aoMudar={recarregar} aoCancelar={() => void cancelar()} />
    </>
  )
}
