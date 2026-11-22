import { useState } from 'react'

import type { PeriodoDosDados } from '../../../application/corporativo/servico'
import { useDemandaDoOrgao } from '../../../application/corporativo/useOrgao'
import type { DemandaDoOrgao } from '../../../domain/corporativo'
import { FILTROS_PADRAO } from '../../../domain/filtros'
import { formatarNumero, formatarPeriodo } from '../../../domain/formatacao'
import {
  NOMES_CURTOS_DAS_FONTES,
  ORDEM_DAS_FONTES,
  type CodigoDaFonte,
} from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { BarrasEmpilhadas } from '../../charts/BarrasEmpilhadas'
import { BarrasHorizontais } from '../../charts/BarrasHorizontais'
import { CORES_DAS_FONTES } from '../../charts/estilo'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { Cartao } from '../../components/Cartao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { Colunas } from '../../components/Secao'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Corporativo.module.css'
import { MapaDasOcorrencias } from './MapaDasOcorrencias'

const PRIMEIRO_ANO_DA_BASE = 2012
const ULTIMO_ANO_DA_BASE = 2026
const ANOS = Array.from(
  { length: ULTIMO_ANO_DA_BASE - PRIMEIRO_ANO_DA_BASE + 1 },
  (_, indice) => PRIMEIRO_ANO_DA_BASE + indice,
)

function nota(demanda: DemandaDoOrgao): string {
  const periodo = formatarPeriodo(demanda.anoInicio, demanda.anoFim)
  return `Fonte: base aberta do RecifeView (156, Ouvidoria, Câmara, Defesa Civil e SEDEC), ${periodo}, registros com o órgão escrito como ${demanda.nomesNaFonte.join(', ')}. Ações proativas da Defesa Civil ficam de fora. n = ${formatarNumero(demanda.total)}.`
}

function PorAno({ demanda }: { demanda: DemandaDoOrgao }) {
  const fontes = ORDEM_DAS_FONTES.filter((fonte) =>
    demanda.porAno.some((item) => item.fonte === fonte),
  )
  const anos = [...new Set(demanda.porAno.map((item) => item.ano))]
  const dados = anos.map((ano) => {
    const linha: Record<string, number | string> = { ano: String(ano) }
    demanda.porAno
      .filter((item) => item.ano === ano)
      .forEach((item) => {
        linha[item.fonte] = item.quantidade
      })
    return linha
  })
  return (
    <BarrasEmpilhadas
      dados={dados}
      eixo="ano"
      orientacao="vertical"
      segmentos={fontes.map((fonte: CodigoDaFonte) => ({
        chave: fonte,
        rotulo: NOMES_CURTOS_DAS_FONTES[fonte],
        cor: CORES_DAS_FONTES[fonte],
      }))}
      formatar={(valor) => formatarNumero(valor)}
      altura={260}
    />
  )
}

function Rotulos({ itens, unidade }: { itens: DemandaDoOrgao['porTema']; unidade: string }) {
  const maximo = Math.max(1, ...itens.map((item) => item.quantidade))
  return (
    <BarrasHorizontais
      dados={itens.map((item) => ({
        chave: item.rotulo,
        rotulo: nomeDaCategoria(item.rotulo),
        valor: item.quantidade,
        texto: formatarNumero(item.quantidade),
      }))}
      maximo={maximo}
      rotuloDoValor={unidade}
    />
  )
}

function Demanda({ demanda }: { demanda: DemandaDoOrgao }) {
  const fontes = new Set(demanda.porAno.map((item) => item.fonte)).size
  const temaPrincipal = demanda.porTema[0]
  if (demanda.total === 0) {
    return (
      <p>
        A base não tem registros com o nome de {demanda.nomeDoOrgao} entre{' '}
        {formatarPeriodo(demanda.anoInicio, demanda.anoFim)}.
      </p>
    )
  }
  return (
    <div className={estilos.pagina}>
      <GradeDeKpis>
        <KpiCard
          rotulo="Registros na base"
          valor={formatarNumero(demanda.total)}
          contexto={formatarPeriodo(demanda.anoInicio, demanda.anoFim)}
        />
        <KpiCard
          rotulo="Fontes"
          valor={formatarNumero(fontes)}
          contexto="canais em que o órgão aparece"
        />
        <KpiCard
          rotulo="Tema mais citado"
          valor={temaPrincipal ? nomeDaCategoria(temaPrincipal.rotulo) : 'sem tema'}
          contexto={temaPrincipal ? `${formatarNumero(temaPrincipal.quantidade)} registros` : ''}
        />
        <KpiCard
          rotulo="Sem bairro"
          valor={formatarNumero(demanda.semBairro)}
          contexto="registros fora do mapa, como os da Ouvidoria, que não traz bairro"
        />
      </GradeDeKpis>
      <Colunas proporcao="larga">
        <Cartao titulo="Registros por ano, em cada fonte" nota={nota(demanda)}>
          <PorAno demanda={demanda} />
        </Cartao>
        <Cartao titulo="Temas mais citados" nota={nota(demanda)}>
          <Rotulos itens={demanda.porTema} unidade="registros" />
        </Cartao>
      </Colunas>
      <Colunas proporcao="larga">
        <Cartao
          titulo="Onde o órgão mais aparece"
          nota={nota(demanda)}
          leitura="Quantidade de registros por bairro, sem dividir pela população. Mais registro não quer dizer mais problema."
        >
          <MapaDasOcorrencias
            rotulo={`Registros com o nome de ${demanda.nomeDoOrgao} por bairro`}
            contagens={demanda.porBairro}
            unidade={['registro', 'registros']}
          />
        </Cartao>
        <Cartao titulo="Situação na fonte" nota={nota(demanda)}>
          <Rotulos itens={demanda.porSituacao} unidade="registros" />
        </Cartao>
      </Colunas>
    </div>
  )
}

export function PaginaDadosDoOrgao() {
  useTituloDaPagina('Dados do órgão')
  const [periodo, definirPeriodo] = useState<PeriodoDosDados>({
    anoInicio: FILTROS_PADRAO.anoInicio,
    anoFim: FILTROS_PADRAO.anoFim,
  })
  const demanda = useDemandaDoOrgao(periodo)
  const mudar = (parcial: Partial<PeriodoDosDados>) => definirPeriodo({ ...periodo, ...parcial })

  return (
    <div className={estilos.pagina}>
      <CabecalhoDaTela titulo="O que a base aberta registra sobre o órgão">
        Pedidos e indicações das fontes públicas do Recife que citam o órgão, para ver onde e em que
        temas ele mais aparece.
      </CabecalhoDaTela>
      <div className={estilos.filtros}>
        <label>
          De
          <select
            value={periodo.anoInicio}
            onChange={(evento) => mudar({ anoInicio: Number(evento.target.value) })}
          >
            {ANOS.map((ano) => (
              <option key={ano} value={ano}>
                {ano}
              </option>
            ))}
          </select>
        </label>
        <label>
          Até
          <select
            value={periodo.anoFim}
            onChange={(evento) => mudar({ anoFim: Number(evento.target.value) })}
          >
            {ANOS.map((ano) => (
              <option key={ano} value={ano}>
                {ano}
              </option>
            ))}
          </select>
        </label>
      </div>
      <EstadoDaConsulta consulta={consultaDoCarregamento(demanda)}>
        {(dados) => <Demanda demanda={dados} />}
      </EstadoDaConsulta>
    </div>
  )
}
