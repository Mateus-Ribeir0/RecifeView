import { Link } from 'react-router'

import { podeEncaminharDeNovo } from '../../../../domain/encaminhamentos'
import type { OcorrenciaClassificada } from '../../../../domain/prioridade'
import { Botao } from '../../../components/Botao'
import { SeloDoEncaminhamento } from '../../encaminhamentos/SeloDoEncaminhamento'
import estilos from './PaginaPrioridade.module.css'

interface Propriedades {
  item: OcorrenciaClassificada
  aoEscolher: (item: OcorrenciaClassificada) => void
}

export function AcaoDeEncaminhar({ item, aoEscolher }: Propriedades) {
  const { encaminhamento } = item
  const botao = item.chaveRegistro ? (
    <Botao variante="secundario" compacto onClick={() => aoEscolher(item)}>
      {encaminhamento ? 'Encaminhar de novo' : 'Encaminhar'}
    </Botao>
  ) : null
  if (!encaminhamento) return botao
  return (
    <span className={estilos.encaminhamento}>
      <Link to={`/painel/encaminhamentos/${encaminhamento.id}`}>{encaminhamento.nomeDoOrgao}</Link>
      <SeloDoEncaminhamento situacao={encaminhamento.situacao} />
      {podeEncaminharDeNovo(encaminhamento.situacao) && botao}
    </span>
  )
}
