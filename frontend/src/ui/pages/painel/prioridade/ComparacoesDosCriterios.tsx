import {
  chaveDoPar,
  OPCOES_DA_ESCALA,
  rotuloDaOpcao,
  type ChaveDoCriterio,
  type Comparacoes,
  type Criterio,
} from '../../../../domain/prioridade'
import { Botao } from '../../../components/Botao'
import estilos from './PaginaPrioridade.module.css'

interface Propriedades {
  criterios: readonly Criterio[]
  pares: readonly (readonly [ChaveDoCriterio, ChaveDoCriterio])[]
  comparacoes: Comparacoes
  aoMudar: (par: string, opcao: number) => void
  aoRestaurar: () => void
}

export function ComparacoesDosCriterios({
  criterios,
  pares,
  comparacoes,
  aoMudar,
  aoRestaurar,
}: Propriedades) {
  const nome = (chave: ChaveDoCriterio) =>
    criterios.find((item) => item.chave === chave)?.nome ?? chave

  return (
    <div className={estilos.comparacoes}>
      {pares.map(([primeiro, segundo]) => {
        const par = chaveDoPar(primeiro, segundo)
        const opcao = comparacoes[par] ?? 1
        const rotulo = rotuloDaOpcao(opcao, nome(primeiro), nome(segundo))
        return (
          <label key={par} className={estilos.comparacao}>
            <span className={estilos.parDeCriterios}>
              <span>{nome(segundo)}</span>
              <strong>{rotulo}</strong>
              <span>{nome(primeiro)}</span>
            </span>
            <input
              type="range"
              min={0}
              max={OPCOES_DA_ESCALA.length - 1}
              value={OPCOES_DA_ESCALA.indexOf(opcao)}
              aria-valuetext={rotulo}
              aria-label={`${nome(primeiro)} comparado a ${nome(segundo)}`}
              onChange={(evento) =>
                aoMudar(par, OPCOES_DA_ESCALA[Number(evento.target.value)] ?? 1)
              }
            />
          </label>
        )
      })}
      <Botao variante="secundario" compacto onClick={aoRestaurar}>
        Voltar à proposta inicial do grupo
      </Botao>
    </div>
  )
}
