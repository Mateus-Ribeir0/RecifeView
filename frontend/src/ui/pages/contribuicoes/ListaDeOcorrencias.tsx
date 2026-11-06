import {
  ROTULOS_DAS_SITUACOES,
  descreverEndereco,
  type OcorrenciaDoPainel,
  type PaginaDeOcorrencias,
} from '../../../domain/contribuicoes'
import { formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import estilos from './Contribuicoes.module.css'

const OCORRENCIAS_POR_PAGINA = 50

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
}

export function ListaDeOcorrencias({ pagina, deslocamento, aoMudarDeslocamento }: Propriedades) {
  if (pagina.itens.length === 0) {
    return <p className={estilos.vazio}>Nenhum relato recebido até agora.</p>
  }
  return (
    <>
      <Tabela
        legenda="Ocorrências do formulário público"
        colunas={COLUNAS}
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
