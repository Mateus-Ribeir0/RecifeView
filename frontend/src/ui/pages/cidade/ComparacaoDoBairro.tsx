import type { CSSProperties, ReactNode } from 'react'

import { useIndicadoresDoBairro } from '../../../application/informacao/useInformacao'
import type { Comparacao, IndicadoresDoBairro } from '../../../domain/cidade'
import { formatarNumero } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useVisivelNaTela } from '../../components/useVisivelNaTela'
import estilos from './Cidade.module.css'

interface Indicador {
  titulo: string
  comparacao: Comparacao
  formatar: (valor: number) => string
  explicacao: string
}

function leituraDaComparacao({ bairro, recife }: Comparacao): string {
  if (bairro === null || recife === null) return 'Sem dado suficiente para comparar.'
  if (Math.abs(bairro - recife) / Math.max(recife, 1) < 0.05) return 'Perto da média do Recife.'
  return bairro > recife ? 'Acima do Recife.' : 'Abaixo do Recife.'
}

function CartaoDeComparacao({ titulo, comparacao, formatar, explicacao }: Indicador) {
  const [referencia, visivel] = useVisivelNaTela<HTMLElement>()
  const maior = Math.max(comparacao.bairro ?? 0, comparacao.recife ?? 0, 1)
  const linhas = [
    { rotulo: 'Bairro', valor: comparacao.bairro, foco: true },
    { rotulo: 'Recife', valor: comparacao.recife, foco: false },
  ]
  return (
    <article ref={referencia} className={estilos.comparacao} data-visivel={visivel || undefined}>
      <h2>{titulo}</h2>
      <p className={`numero ${estilos.valorDaComparacao}`}>
        {comparacao.bairro === null ? 'sem dado' : formatar(comparacao.bairro)}
      </p>
      <p className={estilos.leitura}>{leituraDaComparacao(comparacao)}</p>
      <div className={estilos.barras}>
        {linhas.map(({ rotulo, valor, foco }) => (
          <div key={rotulo} className={estilos.linhaDaBarra}>
            <span>{rotulo}</span>
            <span className={estilos.trilho}>
              <span
                className={estilos.barra}
                data-foco={foco || undefined}
                style={{ '--tamanho': `${((valor ?? 0) / maior) * 100}%` } as CSSProperties}
              />
            </span>
            <span className="numero">{valor === null ? 'sem dado' : formatar(valor)}</span>
          </div>
        ))}
      </div>
      <p className={estilos.leitura}>{explicacao}</p>
    </article>
  )
}

interface Propriedades {
  bairro: string
  acao?: (indicadores: IndicadoresDoBairro) => ReactNode
}

export function ComparacaoDoBairro({ bairro, acao }: Propriedades) {
  const { dados, erro, carregando } = useIndicadoresDoBairro(bairro)
  if (erro) {
    return (
      <Aviso tipo="erro" titulo="Não foi possível carregar o bairro">
        {mensagemDeFalha(erro)}
      </Aviso>
    )
  }
  if (carregando || !dados) return <div className={estilos.esqueleto} aria-busy="true" />
  const periodo = `${dados.anoInicio} a ${dados.anoFim}`
  const indicadores: Indicador[] = [
    {
      titulo: 'Pedidos à Central 156 por mil moradores, por ano',
      comparacao: dados.pedidosPorMilHabitantes,
      formatar: (valor) => formatarNumero(valor, 1),
      explicacao: 'Taxa, e não total, para comparar bairros de tamanhos diferentes.',
    },
    {
      titulo: 'Prazo típico de atendimento (mediana)',
      comparacao: dados.prazoMediano,
      formatar: (valor) => `${formatarNumero(valor)} dias`,
      explicacao: 'Metade dos pedidos atendidos foi resolvida em até este tempo.',
    },
    {
      titulo: 'Prazo dos 10% mais demorados (p90)',
      comparacao: dados.prazoP90,
      formatar: (valor) => `${formatarNumero(valor)} dias`,
      explicacao: 'Mostra a demora que a mediana esconde.',
    },
    {
      titulo: 'Pedidos num local e serviço já pedidos antes',
      comparacao: dados.pctLocalRepetido,
      formatar: (valor) => `${formatarNumero(valor, 1)}%`,
      explicacao: 'Quando o problema volta ao mesmo endereço, só pedidos com número.',
    },
  ]
  return (
    <>
      <p className={estilos.subtitulo}>
        RPA {dados.rpa} · {formatarNumero(dados.populacao)} moradores (Censo 2022) ·{' '}
        {formatarNumero(dados.pedidosAo156)} pedidos à Central 156 de {periodo}. {acao?.(dados)}
      </p>
      <div className={estilos.comparacoes}>
        {indicadores.map((indicador) => (
          <CartaoDeComparacao key={indicador.titulo} {...indicador} />
        ))}
      </div>
      <p className={estilos.nota}>
        Fonte: Central 156/Emlurb (Portal de Dados Abertos do Recife, ODbL), {periodo}. Prazos só de
        pedidos atendidos. Bairros com menos de 1.000 moradores não têm taxa, porque ela distorce.
        Mais pedidos não quer dizer mais problema: pode ser mais confiança no canal.
      </p>
    </>
  )
}
