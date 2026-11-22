import { ContextoDosAcessos } from '../../application/acessos/contexto'
import { ProvedorDoPainel } from '../../application/consultas/ProvedorDoPainel'
import { ContextoDosEncaminhamentos } from '../../application/encaminhamentos/contexto'
import { ProvedorDeFiltros } from '../../application/filtros/ProvedorDeFiltros'
import { ContextoDasImportacoes } from '../../application/importacoes/contexto'
import { LayoutDoPainel } from '../pages/painel/LayoutDoPainel'
import {
  servicoDeAcessos,
  servicoDeEncaminhamentos,
  servicoDeImportacoes,
  servicoDoPainel,
} from './servicos'

export function MontagemDoPainel() {
  return (
    <ProvedorDoPainel servico={servicoDoPainel}>
      <ContextoDasImportacoes value={servicoDeImportacoes}>
        <ContextoDosEncaminhamentos value={servicoDeEncaminhamentos}>
          <ContextoDosAcessos value={servicoDeAcessos}>
            <ProvedorDeFiltros>
              <LayoutDoPainel />
            </ProvedorDeFiltros>
          </ContextoDosAcessos>
        </ContextoDosEncaminhamentos>
      </ContextoDasImportacoes>
    </ProvedorDoPainel>
  )
}
