import { useSearchParams } from 'react-router'

import { useFilaDoOrgao } from '../../../application/corporativo/useOrgao'
import {
  ABAS_DO_ORGAO,
  PEDIDO_INICIAL_DA_FILA,
  ROTULOS_DAS_ABAS,
  type AbaDoOrgao,
  type FilaDoOrgao,
  type PedidoDaFila,
} from '../../../domain/corporativo'
import { contar, formatarNumero } from '../../../domain/formatacao'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Botao } from '../../components/Botao'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { CartaoDaOcorrencia } from './CartaoDaOcorrencia'
import estilos from './Corporativo.module.css'
import { useNomeDoBairro } from './useNomeDoBairro'

const ITENS_POR_PAGINA = 30
const MENSAGENS_DE_VAZIO: Readonly<Record<AbaDoOrgao, string>> = {
  novas: 'Nenhuma ocorrência esperando a primeira resposta.',
  em_atendimento: 'Nenhuma ocorrência em atendimento.',
  vencidas: 'Nenhuma ocorrência com prazo vencido.',
  resolvidas: 'O órgão ainda não resolveu nenhuma ocorrência pelo RecifeView.',
  devolvidas: 'Nenhuma ocorrência devolvida à gestão.',
  todas: 'Nenhuma ocorrência encaminhada a este órgão.',
}

function lerPedido(params: URLSearchParams): PedidoDaFila {
  const aba = params.get('aba')
  return {
    aba: ABAS_DO_ORGAO.includes(aba as AbaDoOrgao)
      ? (aba as AbaDoOrgao)
      : PEDIDO_INICIAL_DA_FILA.aba,
    bairro: params.get('bairro'),
    categoria: params.get('categoria'),
    deslocamento: Math.max(Number(params.get('deslocamento') ?? 0) || 0, 0),
  }
}

function paramsDoPedido(pedido: PedidoDaFila): Record<string, string> {
  const params: Record<string, string> = { aba: pedido.aba }
  if (pedido.bairro) params.bairro = pedido.bairro
  if (pedido.categoria) params.categoria = pedido.categoria
  if (pedido.deslocamento) params.deslocamento = String(pedido.deslocamento)
  return params
}

interface FiltrosProps {
  pedido: PedidoDaFila
  fila: FilaDoOrgao | null
  aoMudar: (pedido: PedidoDaFila) => void
}

function Abas({ pedido, fila, aoMudar }: FiltrosProps) {
  return (
    <div className={estilos.abas} role="group" aria-label="Etapa das ocorrências">
      {ABAS_DO_ORGAO.map((aba) => {
        const quantidade = fila?.porAba[aba]
        const alerta = aba === 'vencidas' && (quantidade ?? 0) > 0
        return (
          <button
            key={aba}
            type="button"
            className={estilos.aba}
            aria-pressed={pedido.aba === aba}
            onClick={() => aoMudar({ ...pedido, aba, deslocamento: 0 })}
          >
            {ROTULOS_DAS_ABAS[aba]}
            {quantidade !== undefined && (
              <span
                className={`${estilos.contagem} ${alerta ? estilos.contagemDeAlerta : ''} numero`}
              >
                {formatarNumero(quantidade)}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}

function Filtros({ pedido, fila, aoMudar }: FiltrosProps) {
  const nomeDoBairro = useNomeDoBairro()
  const mudar = (parcial: Partial<PedidoDaFila>) =>
    aoMudar({ ...pedido, ...parcial, deslocamento: 0 })
  return (
    <div className={estilos.filtros}>
      <label>
        Bairro
        <select
          value={pedido.bairro ?? ''}
          onChange={(evento) => mudar({ bairro: evento.target.value || null })}
        >
          <option value="">Todos os bairros</option>
          {fila?.bairros.map((bairro) => (
            <option key={bairro} value={bairro}>
              {nomeDoBairro(bairro)}
            </option>
          ))}
        </select>
      </label>
      <label>
        Tema
        <select
          value={pedido.categoria ?? ''}
          onChange={(evento) => mudar({ categoria: evento.target.value || null })}
        >
          <option value="">Todos os temas</option>
          {fila?.categorias.map((categoria) => (
            <option key={categoria} value={categoria}>
              {nomeDaCategoria(categoria)}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}

interface PaginacaoProps {
  pedido: PedidoDaFila
  total: number
  aoMudar: (pedido: PedidoDaFila) => void
}

function Paginacao({ pedido, total, aoMudar }: PaginacaoProps) {
  if (total <= ITENS_POR_PAGINA) return null
  const inicio = pedido.deslocamento + 1
  const fim = Math.min(pedido.deslocamento + ITENS_POR_PAGINA, total)
  return (
    <div className={estilos.paginacao}>
      <Botao
        variante="secundario"
        compacto
        disabled={pedido.deslocamento === 0}
        onClick={() => aoMudar({ ...pedido, deslocamento: pedido.deslocamento - ITENS_POR_PAGINA })}
      >
        Anteriores
      </Botao>
      <span className={estilos.nota}>
        {formatarNumero(inicio)} a {formatarNumero(fim)} de {formatarNumero(total)}
      </span>
      <Botao
        variante="secundario"
        compacto
        disabled={fim >= total}
        onClick={() => aoMudar({ ...pedido, deslocamento: pedido.deslocamento + ITENS_POR_PAGINA })}
      >
        Próximas
      </Botao>
    </div>
  )
}

export function PaginaOcorrenciasDoOrgao() {
  useTituloDaPagina('Ocorrências do órgão')
  const [params, definirParams] = useSearchParams()
  const pedido = lerPedido(params)
  const fila = useFilaDoOrgao(pedido)
  const nomeDoBairro = useNomeDoBairro()
  const mudar = (novo: PedidoDaFila) => definirParams(paramsDoPedido(novo))

  return (
    <div className={estilos.pagina}>
      <CabecalhoDaTela titulo="Ocorrências">
        Cada ocorrência que a gestão encaminhou ao órgão, da que vence antes para a que vence
        depois. Abra uma para ver onde fica e responder.
      </CabecalhoDaTela>
      <Abas pedido={pedido} fila={fila.dados} aoMudar={mudar} />
      <Filtros pedido={pedido} fila={fila.dados} aoMudar={mudar} />
      <EstadoDaConsulta
        consulta={consultaDoCarregamento(fila)}
        estaVazia={(dados) => dados.itens.length === 0}
        mensagemDeVazio={MENSAGENS_DE_VAZIO[pedido.aba]}
      >
        {(dados) => (
          <>
            <p className={estilos.nota}>
              {contar(dados.total, 'ocorrência', 'ocorrências')} em{' '}
              {ROTULOS_DAS_ABAS[pedido.aba].toLowerCase()}
              {pedido.bairro && `, ${nomeDoBairro(pedido.bairro)}`}
              {pedido.categoria && `, ${nomeDaCategoria(pedido.categoria).toLowerCase()}`}.
            </p>
            <ul className={estilos.lista}>
              {dados.itens.map((item) => (
                <li key={item.id}>
                  <CartaoDaOcorrencia item={item} nomeDoBairro={nomeDoBairro} />
                </li>
              ))}
            </ul>
            <Paginacao pedido={pedido} total={dados.total} aoMudar={mudar} />
          </>
        )}
      </EstadoDaConsulta>
    </div>
  )
}
