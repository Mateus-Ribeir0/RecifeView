import { useCatalogo } from '../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../application/filtros/contexto'
import { estaNoPadrao } from '../../../domain/filtros'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Icone } from '../../components/Icone'
import type { FiltroDaTela } from '../../conteudo/telasDoPainel'
import estilos from './BarraDeFiltros.module.css'
import { ControleDePeriodo } from './ControleDePeriodo'
import { SeletorDeRpa } from './SeletorDeRpa'
import { SeletorMultiplo } from './SeletorMultiplo'

export function BarraDeFiltros({ campos }: { campos: readonly FiltroDaTela[] }) {
  const { filtros, alterar, limpar } = useFiltrosGlobais()
  const { dados: catalogo } = useCatalogo()
  if (!catalogo) return <div className={estilos.barra} />

  const bairrosDaRpa = catalogo.bairros.filter(
    (bairro) => filtros.rpas.length === 0 || filtros.rpas.includes(bairro.rpa),
  )

  function alterarRpas(rpas: string[]) {
    const validos = new Set(
      catalogo?.bairros
        .filter((bairro) => rpas.length === 0 || rpas.includes(bairro.rpa))
        .map((bairro) => bairro.bairroOficial),
    )
    alterar({ rpas, bairros: filtros.bairros.filter((bairro) => validos.has(bairro)) })
  }

  return (
    <section className={estilos.barra} aria-label="Filtros">
      <span className={estilos.icone}>
        <Icone nome="filtro" tamanho={18} />
      </span>
      {campos.includes('periodo') && (
        <ControleDePeriodo
          minimo={catalogo.anoMinimo}
          maximo={catalogo.anoMaximo}
          inicio={filtros.anoInicio}
          fim={filtros.anoFim}
          aoMudar={(anoInicio, anoFim) => alterar({ anoInicio, anoFim })}
        />
      )}
      {campos.includes('rpa') && (
        <SeletorDeRpa rpas={catalogo.rpas} selecionadas={filtros.rpas} aoMudar={alterarRpas} />
      )}
      {campos.includes('bairro') && (
        <SeletorMultiplo
          rotulo="Bairro"
          nenhum="Todos"
          opcoes={bairrosDaRpa.map((bairro) => ({
            valor: bairro.bairroOficial,
            rotulo: bairro.nome,
          }))}
          selecionados={filtros.bairros}
          aoMudar={(bairros) => alterar({ bairros })}
        />
      )}
      {campos.includes('categoria') && (
        <SeletorMultiplo
          rotulo="Categoria"
          nenhum="Todas"
          opcoes={catalogo.categorias.map((categoria) => ({
            valor: categoria,
            rotulo: nomeDaCategoria(categoria),
          }))}
          selecionados={filtros.categorias}
          aoMudar={(categorias) => alterar({ categorias })}
        />
      )}
      {!estaNoPadrao(filtros) && (
        <button type="button" className={estilos.limpar} onClick={limpar}>
          Limpar
        </button>
      )}
    </section>
  )
}
