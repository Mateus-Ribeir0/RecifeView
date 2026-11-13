import { ROTULOS_DAS_ETAPAS } from '../../../domain/encaminhamentos'
import { formatarData, formatarDataEHora } from '../../../domain/formatacao'
import { nomeDaCategoria } from '../../../domain/nomes'
import type { AndamentoDoPedido, EncaminhamentoPublico } from '../../../domain/pedidos'
import { SeloDoEncaminhamento } from '../encaminhamentos/SeloDoEncaminhamento'
import estilos from './Pedidos.module.css'

export function EtapasDoEncaminhamento({ item }: { item: EncaminhamentoPublico }) {
  return (
    <div className={estilos.encaminhamento}>
      <p>
        Encaminhado para <strong>{item.nomeDoOrgao}</strong> em {formatarData(item.encaminhadoEm)}.{' '}
        <SeloDoEncaminhamento situacao={item.situacao} atrasado={item.atrasado} />
      </p>
      <ol className={estilos.etapas} aria-label={`Etapas do encaminhamento ${item.codigo}`}>
        {item.etapas.map((etapa, indice) => (
          <li key={`${etapa.ocorridoEm}-${indice}`}>
            <span>{ROTULOS_DAS_ETAPAS[etapa.situacao]}</span>
            <time dateTime={etapa.ocorridoEm}>{formatarDataEHora(etapa.ocorridoEm)}</time>
          </li>
        ))}
      </ol>
      <p className={estilos.nota}>
        {item.protocoloDoOrgao
          ? `Protocolo no órgão: ${item.protocoloDoOrgao}.`
          : 'O órgão ainda não informou um protocolo próprio.'}{' '}
        Prazo para resolver ou devolver: {formatarData(item.prazoDeResposta)}.
      </p>
    </div>
  )
}

export function CartaoDoAndamento({ andamento }: { andamento: AndamentoDoPedido }) {
  const assunto = andamento.servico ?? andamento.categoria
  return (
    <article className={estilos.cartao}>
      <header>
        <p className={estilos.fonte}>
          {andamento.rotuloDaFonte} · protocolo {andamento.protocolo}
        </p>
        <h3>{nomeDaCategoria(assunto)}</h3>
      </header>
      <dl className={estilos.dados}>
        <div>
          <dt>Aberto em</dt>
          <dd>{formatarData(andamento.dataAbertura)}</dd>
        </div>
        <div>
          <dt>Situação na fonte</dt>
          <dd>{nomeDaCategoria(andamento.situacao)}</dd>
        </div>
        <div>
          <dt>Último movimento</dt>
          <dd>{formatarData(andamento.dataUltMovimento)}</dd>
        </div>
        {andamento.prazoDaFonte && (
          <div>
            <dt>Prazo da fonte</dt>
            <dd>{formatarData(andamento.prazoDaFonte)}</dd>
          </div>
        )}
      </dl>
      {andamento.encaminhamentos.length > 0 ? (
        andamento.encaminhamentos.map((item) => (
          <EtapasDoEncaminhamento key={item.codigo} item={item} />
        ))
      ) : (
        <p className={estilos.nota}>
          A gestão ainda não encaminhou este pedido a outro órgão pelo RecifeView.
        </p>
      )}
    </article>
  )
}
