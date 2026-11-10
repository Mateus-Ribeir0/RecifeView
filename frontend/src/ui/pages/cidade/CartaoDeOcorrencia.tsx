import {
  descreverLocal,
  EXPLICACOES_DAS_SITUACOES,
  haQuantoTempo,
  ROTULOS_DAS_SITUACOES,
  type OcorrenciaDaCidade,
  type SituacaoPublica,
} from '../../../domain/cidade'
import { contar } from '../../../domain/formatacao'
import { Icone, type NomeDoIcone } from '../../components/Icone'
import estilos from './Cidade.module.css'

const ICONES_DOS_TEMAS: Readonly<Record<string, NomeDoIcone>> = {
  Iluminação: 'lampada',
  'Limpeza e coleta': 'limpeza',
  Árvores: 'arvore',
  'Drenagem e canais': 'gota',
  'Ruas e calçadas': 'via',
}

export function IconeDoTema({ tema }: { tema: string }) {
  return (
    <span className={estilos.iconeDoTema} aria-hidden="true">
      <Icone nome={ICONES_DOS_TEMAS[tema] ?? 'relato'} tamanho={22} />
    </span>
  )
}

const ICONES_DAS_SITUACOES: Readonly<Record<SituacaoPublica, NomeDoIcone>> = {
  recebido: 'relato',
  em_analise: 'pessoas',
  no_painel: 'telas',
  coberto_por_pedido_oficial: 'confirmado',
}

export function SeloDaSituacao({ situacao }: { situacao: SituacaoPublica }) {
  return (
    <span
      className={estilos.situacao}
      data-situacao={situacao}
      title={EXPLICACOES_DAS_SITUACOES[situacao]}
    >
      <Icone nome={ICONES_DAS_SITUACOES[situacao]} tamanho={14} />
      {ROTULOS_DAS_SITUACOES[situacao]}
    </span>
  )
}

interface Propriedades {
  ocorrencia: OcorrenciaDaCidade
  hoje: Date
}

export function CartaoDeOcorrencia({ ocorrencia, hoje }: Propriedades) {
  return (
    <article className={estilos.cartao}>
      <IconeDoTema tema={ocorrencia.tema} />
      <div className={estilos.corpoDoCartao}>
        <div className={estilos.topoDoCartao}>
          <h3>{ocorrencia.servico}</h3>
          <SeloDaSituacao situacao={ocorrencia.situacao} />
        </div>
        <p className={estilos.local}>{descreverLocal(ocorrencia)}</p>
        <p className={estilos.detalhe}>
          {ocorrencia.bairro}, RPA {ocorrencia.rpa} · relatado{' '}
          {haQuantoTempo(ocorrencia.dataRelato, hoje)}
        </p>
        <ul className={estilos.contagens}>
          <li>
            <Icone nome="pessoas" tamanho={16} />
            {contar(ocorrencia.relatos, 'pessoa relatou', 'pessoas relataram')}
          </li>
          {ocorrencia.semRetorno > 0 && (
            <li>
              <Icone nome="relogio" tamanho={16} />
              {contar(
                ocorrencia.semRetorno,
                'já pediu e não teve retorno',
                'já pediram e não tiveram retorno',
              )}
            </li>
          )}
        </ul>
      </div>
    </article>
  )
}
