import { Link } from 'react-router'

import { ETAPAS_NO_ORGAO } from '../../../domain/corporativo'
import type { MesmoProblema, SituacaoDoEncaminhamento } from '../../../domain/encaminhamentos'
import { contar, formatarData } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { SeloDoEncaminhamento } from '../encaminhamentos/SeloDoEncaminhamento'
import estilos from './Corporativo.module.css'

interface Propriedades {
  parecidos: readonly MesmoProblema[]
  registrosDoMesmoLocal: number
  fonte: string
  caminhoDoDetalhe: (id: number) => string
  rotulosDasEtapas?: Readonly<Record<SituacaoDoEncaminhamento, string>>
}

function descreverParecido(item: MesmoProblema): string {
  const classe = item.certo ? 'Mesma ocorrência' : 'Provável'
  return `${classe}: ${item.motivos.join(', ').toLowerCase()}. Aberta em ${formatarData(item.dataAbertura)}.`
}

/** Outras ocorrências do mesmo problema: as do órgão abrem; as de outro órgão só dizem onde estão. */
export function ListaDoMesmoProblema({
  parecidos,
  registrosDoMesmoLocal,
  fonte,
  caminhoDoDetalhe,
  rotulosDasEtapas = ETAPAS_NO_ORGAO,
}: Propriedades) {
  return (
    <div className={estilos.coluna}>
      {parecidos.length === 0 ? (
        <p>Nenhuma outra ocorrência encaminhada para o mesmo problema.</p>
      ) : (
        <ul className={estilos.parecidos}>
          {parecidos.map((item, indice) => (
            <li key={item.id ?? `outro-${indice}`}>
              {item.id !== null && item.codigo ? (
                <Link to={caminhoDoDetalhe(item.id)}>{item.codigo}</Link>
              ) : (
                <span>{item.nomeDoOrgao}</span>
              )}
              <SeloDoEncaminhamento
                situacao={item.situacao}
                atrasado={item.atrasado}
                rotulo={rotulosDasEtapas[item.situacao]}
              />
              <span className={estilos.nota}>{descreverParecido(item)}</span>
            </li>
          ))}
        </ul>
      )}
      <p className={estilos.nota}>
        {registrosDoMesmoLocal > 0
          ? `Na base de ${nomeDaFonte(fonte)}, mais ${contar(registrosDoMesmoLocal, 'registro', 'registros')} do mesmo local e tema em até 30 dias, encaminhados ou não.`
          : `Na base de ${nomeDaFonte(fonte)}, nenhum outro registro do mesmo local e tema em até 30 dias.`}{' '}
        Mesmo problema: mesma fonte, bairro e tema, menos de 30 dias de diferença e o mesmo local,
        pela regra do pente fino.
      </p>
    </div>
  )
}
