import { useCatalogo } from '../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../application/filtros/contexto'
import { estaNoPadrao } from '../../../domain/filtros'
import { nomeDaCategoria } from '../../../domain/nomes'
import { RPAS } from '../../../domain/territorio'
import { Botao } from '../../components/Botao'
import { ControleDePeriodo } from './ControleDePeriodo'
import estilos from './FiltrosGlobais.module.css'
import { SeletorMultiplo } from './SeletorMultiplo'

function rotuloDaRpa(rpa: string): string {
  const nome = RPAS.find((item) => String(item.numero) === rpa)?.nome
  return nome ? `RPA ${rpa} (${nome})` : `RPA ${rpa}`
}

export function FiltrosGlobais() {
  const { filtros, alterar, limpar } = useFiltrosGlobais()
  const { dados: catalogo } = useCatalogo()
  if (!catalogo) return null

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
    <section className={estilos.filtros} aria-labelledby="titulo-dos-filtros">
      <h2 id="titulo-dos-filtros" className={estilos.titulo}>
        Filtros
      </h2>
      <ControleDePeriodo
        minimo={catalogo.anoMinimo}
        maximo={catalogo.anoMaximo}
        inicio={filtros.anoInicio}
        fim={filtros.anoFim}
        aoMudar={(anoInicio, anoFim) => alterar({ anoInicio, anoFim })}
      />
      <SeletorMultiplo
        rotulo="RPA"
        placeholder="Todas"
        opcoes={catalogo.rpas.map((rpa) => ({ valor: rpa, rotulo: rotuloDaRpa(rpa) }))}
        selecionados={filtros.rpas}
        aoMudar={alterarRpas}
      />
      <SeletorMultiplo
        rotulo="Bairro"
        placeholder="Todos"
        opcoes={bairrosDaRpa.map((bairro) => ({
          valor: bairro.bairroOficial,
          rotulo: bairro.nome,
        }))}
        selecionados={filtros.bairros}
        aoMudar={(bairros) => alterar({ bairros })}
      />
      <SeletorMultiplo
        rotulo="Categoria de serviço"
        placeholder="Todas"
        opcoes={catalogo.categorias.map((categoria) => ({
          valor: categoria,
          rotulo: nomeDaCategoria(categoria),
        }))}
        selecionados={filtros.categorias}
        aoMudar={(categorias) => alterar({ categorias })}
      />
      <Botao
        variante="secundario"
        compacto
        larguraTotal
        disabled={estaNoPadrao(filtros)}
        onClick={limpar}
      >
        Limpar filtros
      </Botao>
    </section>
  )
}
