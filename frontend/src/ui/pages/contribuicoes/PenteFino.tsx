import { useState } from 'react'

import { useServicoDeContribuicoes } from '../../../application/contribuicoes/contexto'
import {
  descreverEndereco,
  type DecisaoDoPar,
  type LadoDoPar,
  type ParParaRevisar,
} from '../../../domain/contribuicoes'
import { contar, formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Contribuicoes.module.css'

function Lado({ lado, titulo }: { lado: LadoDoPar; titulo: string }) {
  return (
    <div className={estilos.lado}>
      <h3>{titulo}</h3>
      <dl>
        <dt>Problema</dt>
        <dd>{lado.servico}</dd>
        <dt>Local</dt>
        <dd>
          {descreverEndereco(lado)}, {lado.bairro}
        </dd>
        <dt>Recebido</dt>
        <dd>
          {formatarDataEHora(lado.recebidaEm)}, {contar(lado.relatos, 'relato', 'relatos')}
        </dd>
        <dt>Detalhe</dt>
        <dd>{lado.detalhe ?? 'sem detalhe'}</dd>
      </dl>
    </div>
  )
}

interface PropriedadesDoPar {
  par: ParParaRevisar
  aoDecidir: () => void
}

function CartaoDoPar({ par, aoDecidir }: PropriedadesDoPar) {
  const servico = useServicoDeContribuicoes()
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)

  async function decidir(decisao: DecisaoDoPar) {
    definirEnviando(true)
    definirFalha(null)
    try {
      await servico.decidir(par.id, decisao)
      aoDecidir()
    } catch (motivo) {
      definirFalha(motivo)
      definirEnviando(false)
    }
  }

  return (
    <article className={estilos.par}>
      <div className={estilos.motivos}>
        <strong className="numero">Semelhança {formatarNumero(par.pontuacao * 100)}%</strong>
        <ul>
          {par.motivos.map((motivo) => (
            <li key={motivo}>{motivo}</li>
          ))}
        </ul>
      </div>
      <div className={estilos.lados}>
        <Lado lado={par.primeiro} titulo="Relato mais antigo" />
        <Lado lado={par.segundo} titulo="Relato mais novo" />
      </div>
      {falha ? (
        <Aviso tipo="erro" titulo="A decisão não foi salva">
          {mensagemDeFalha(falha)}
        </Aviso>
      ) : null}
      <div className={estilos.acoesDoPar}>
        <Botao compacto disabled={enviando} onClick={() => void decidir('mesma')}>
          É a mesma ocorrência
        </Botao>
        <Botao
          compacto
          variante="secundario"
          disabled={enviando}
          onClick={() => void decidir('diferente')}
        >
          São ocorrências diferentes
        </Botao>
      </div>
    </article>
  )
}

interface Propriedades {
  pares: readonly ParParaRevisar[]
  aoDecidir: () => void
}

export function PenteFino({ pares, aoDecidir }: Propriedades) {
  if (pares.length === 0) {
    return <p className={estilos.vazio}>Nenhuma dupla parecida esperando decisão.</p>
  }
  return (
    <div className={estilos.pares}>
      {pares.map((par) => (
        <CartaoDoPar key={par.id} par={par} aoDecidir={aoDecidir} />
      ))}
    </div>
  )
}
