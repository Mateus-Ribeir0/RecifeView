import { Link } from 'react-router'

import { estaAberta, ETAPAS_NO_ORGAO, type OcorrenciaNaFila } from '../../../domain/corporativo'
import { contar, formatarData } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { SeloDoEncaminhamento } from '../encaminhamentos/SeloDoEncaminhamento'
import estilos from './Corporativo.module.css'
import { PrazoRestante } from './PrazoRestante'

interface Propriedades {
  item: OcorrenciaNaFila
  nomeDoBairro: (bairroOficial: string | null) => string
}

function MarcaDoMesmoProblema({ item }: { item: OcorrenciaNaFila }) {
  const total = item.mesmoProblemaNoOrgao + item.mesmoProblemaEmOutrosOrgaos
  if (total === 0) return null
  const fora = item.mesmoProblemaEmOutrosOrgaos
  return (
    <span className={`${estilos.marca} ${estilos.marcaDoMesmoProblema}`}>
      Mesmo problema: {contar(total, 'outra ocorrência', 'outras ocorrências')}
      {fora > 0 && `, ${contar(fora, 'em outro órgão', 'em outros órgãos')}`}
    </span>
  )
}

export function CartaoDaOcorrencia({ item, nomeDoBairro }: Propriedades) {
  const classe = item.atrasado
    ? estilos.cartaoComAlerta
    : estaAberta(item.situacao)
      ? estilos.cartaoAberto
      : ''
  const caminho = `/corporativo/ocorrencias/${item.id}`
  return (
    <article className={`${estilos.cartao} ${classe}`}>
      <div className={estilos.topoDoCartao}>
        <span className={estilos.codigo}>{item.codigo}</span>
        <SeloDoEncaminhamento
          situacao={item.situacao}
          atrasado={item.atrasado}
          rotulo={ETAPAS_NO_ORGAO[item.situacao]}
        />
        <PrazoRestante item={item} />
      </div>
      <h3 className={estilos.tituloDoCartao}>
        <Link to={caminho}>
          {nomeDaCategoria(item.categoria)}
          {item.servico && `: ${nomeDaCategoria(item.servico)}`}
        </Link>
      </h3>
      <p className={estilos.local}>
        {nomeDoBairro(item.bairroOficial)}
        {item.rpa && ` (RPA ${item.rpa})`}
        {item.localAproximado && `, ${item.localAproximado}`}. Pedido em{' '}
        {formatarData(item.dataAbertura)} ({nomeDaFonte(item.fonte)}).
      </p>
      <div className={estilos.marcas}>
        <MarcaDoMesmoProblema item={item} />
        {item.pessoasQueAcompanham > 0 && (
          <span className={estilos.marca}>
            {contar(item.pessoasQueAcompanham, 'pessoa acompanha', 'pessoas acompanham')}
          </span>
        )}
        {item.previsao && (
          <span className={estilos.marca}>Previsão {formatarData(item.previsao)}</span>
        )}
      </div>
    </article>
  )
}
