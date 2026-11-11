import { Link } from 'react-router'

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
  if (encaminhamento) {
    return (
      <span className={estilos.encaminhamento}>
        <Link to={`/painel/encaminhamentos/${encaminhamento.id}`}>
          {encaminhamento.nomeDoOrgao}
        </Link>
        <SeloDoEncaminhamento situacao={encaminhamento.situacao} />
      </span>
    )
  }
  if (!item.chaveRegistro) return null
  return (
    <Botao variante="secundario" compacto onClick={() => aoEscolher(item)}>
      Encaminhar
    </Botao>
  )
}
