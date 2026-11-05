import { ProvedorDoPainel } from '../../application/consultas/ProvedorDoPainel'
import { ProvedorDeFiltros } from '../../application/filtros/ProvedorDeFiltros'
import { ContextoDasImportacoes } from '../../application/importacoes/contexto'
import { LayoutDoPainel } from '../pages/painel/LayoutDoPainel'
import { servicoDeImportacoes, servicoDoPainel } from './servicos'

export function MontagemDoPainel() {
  return (
    <ProvedorDoPainel servico={servicoDoPainel}>
      <ContextoDasImportacoes value={servicoDeImportacoes}>
        <ProvedorDeFiltros>
          <LayoutDoPainel />
        </ProvedorDeFiltros>
      </ContextoDasImportacoes>
    </ProvedorDoPainel>
  )
}
