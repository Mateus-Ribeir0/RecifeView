import { useState } from 'react'
import { Link } from 'react-router'

import {
  ROTULOS_DAS_SITUACOES,
  descreverEndereco,
  type OcorrenciaDoPainel,
  type PaginaDeOcorrencias,
} from '../../../domain/contribuicoes'
import { podeEncaminharDeNovo } from '../../../domain/encaminhamentos'
import { formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { Botao } from '../../components/Botao'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import { PainelDeEncaminhamento } from '../encaminhamentos/PainelDeEncaminhamento'
import { SeloDoEncaminhamento } from '../encaminhamentos/SeloDoEncaminhamento'
import estilos from './Contribuicoes.module.css'

const OCORRENCIAS_POR_PAGINA = 50
const QUANDO_NAO_ESTA_NA_BASE = 'entra na base depois do pacote'

interface AcaoProps {
  item: OcorrenciaDoPainel
  aoEscolher: (item: OcorrenciaDoPainel) => void
}

function Encaminhamento({ item, aoEscolher }: AcaoProps) {
  const { encaminhamento } = item
  const botao = (
    <Botao variante="secundario" compacto onClick={() => aoEscolher(item)}>
      {encaminhamento ? 'Encaminhar de novo' : 'Encaminhar'}
    </Botao>
  )
  if (!item.chaveRegistro) {
    return <span className={estilos.detalheDaCelula}>{QUANDO_NAO_ESTA_NA_BASE}</span>
  }
  if (!encaminhamento) return botao
  return (
    <span className={estilos.encaminhamento}>
      <Link to={`/painel/encaminhamentos/${encaminhamento.id}`}>{encaminhamento.nomeDoOrgao}</Link>
      <SeloDoEncaminhamento situacao={encaminhamento.situacao} />
      {podeEncaminharDeNovo(encaminhamento.situacao) && botao}
    </span>
  )
}

function colunas(
  aoEscolher: (item: OcorrenciaDoPainel) => void,
): readonly ColunaDaTabela<OcorrenciaDoPainel>[] {
  return [
    ...COLUNAS,
    {
      titulo: 'Órgão',
      ajuda: 'A ocorrência que já está na base pode seguir para o órgão que resolve.',
      valor: (item) => <Encaminhamento item={item} aoEscolher={aoEscolher} />,
    },
  ]
}

const COLUNAS: readonly ColunaDaTabela<OcorrenciaDoPainel>[] = [
  { titulo: 'Recebida', valor: (item) => formatarDataEHora(item.recebidaEm) },
  { titulo: 'Problema', valor: (item) => item.servico },
  {
    titulo: 'Local',
    valor: (item) => (
      <>
        {descreverEndereco(item)}
        <span className={estilos.detalheDaCelula}>{item.bairro}</span>
      </>
    ),
  },
  { titulo: 'Relatos', numerica: true, valor: (item) => formatarNumero(item.relatos) },
  { titulo: 'Sem retorno', numerica: true, valor: (item) => formatarNumero(item.semRetorno) },
  { titulo: 'Situação', valor: (item) => ROTULOS_DAS_SITUACOES[item.situacao] },
]

interface Propriedades {
  pagina: PaginaDeOcorrencias
  deslocamento: number
  aoMudarDeslocamento: (deslocamento: number) => void
  aoEncaminhar: () => void
}

export function ListaDeOcorrencias({
  pagina,
  deslocamento,
  aoMudarDeslocamento,
  aoEncaminhar,
}: Propriedades) {
  const [escolhida, definirEscolhida] = useState<OcorrenciaDoPainel | null>(null)
  if (pagina.itens.length === 0) {
    return <p className={estilos.vazio}>Nenhum relato recebido até agora.</p>
  }
  return (
    <>
      {escolhida?.chaveRegistro && (
        <PainelDeEncaminhamento
          chaveRegistro={escolhida.chaveRegistro}
          nota={null}
          contribuicaoId={escolhida.id}
          aoFechar={() => definirEscolhida(null)}
          aoConcluir={() => {
            definirEscolhida(null)
            aoEncaminhar()
          }}
        />
      )}
      <Tabela
        legenda="Ocorrências do formulário público"
        colunas={colunas(definirEscolhida)}
        linhas={pagina.itens}
        chave={(item) => item.id}
      />
      {pagina.total > OCORRENCIAS_POR_PAGINA && (
        <div className={estilos.paginacao}>
          <button
            type="button"
            disabled={deslocamento === 0}
            onClick={() => aoMudarDeslocamento(deslocamento - OCORRENCIAS_POR_PAGINA)}
          >
            Anteriores
          </button>
          <button
            type="button"
            disabled={deslocamento + OCORRENCIAS_POR_PAGINA >= pagina.total}
            onClick={() => aoMudarDeslocamento(deslocamento + OCORRENCIAS_POR_PAGINA)}
          >
            Próximas
          </button>
        </div>
      )}
    </>
  )
}
