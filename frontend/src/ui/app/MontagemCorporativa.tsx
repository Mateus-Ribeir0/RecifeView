import { ContextoDoOrgao } from '../../application/corporativo/contexto'
import { LayoutCorporativo } from '../pages/corporativo/LayoutCorporativo'
import { servicoDoOrgao } from './servicos'

export function MontagemCorporativa() {
  return (
    <ContextoDoOrgao value={servicoDoOrgao}>
      <LayoutCorporativo />
    </ContextoDoOrgao>
  )
}
