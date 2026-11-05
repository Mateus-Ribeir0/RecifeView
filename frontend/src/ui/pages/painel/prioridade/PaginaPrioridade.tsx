import { useMemo, useState } from 'react'

import { useCriterios, usePrioridade } from '../../../../application/consultas/usePainel'
import { formatarNumero, formatarPorcentagem } from '../../../../domain/formatacao'
import {
  chaveDoPar,
  opcaoDoValor,
  valorDaOpcao,
  type ChaveDoCriterio,
  type Comparacoes,
  type Criterios,
  type Julgamento,
  type Prioridade,
  type TesteDeSensibilidade,
} from '../../../../domain/prioridade'
import { BarrasHorizontais } from '../../../charts/BarrasHorizontais'
import { Abas } from '../../../components/Abas'
import { Aviso } from '../../../components/Aviso'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { KpiCard } from '../../../components/KpiCard'
import { Colunas, Secao } from '../../../components/Secao'
import { Tabela } from '../../../components/Tabela'
import { useValorAtrasado } from '../../../components/useValorAtrasado'
import { ComparacoesDosCriterios } from './ComparacoesDosCriterios'
import { CORES_DOS_CRITERIOS } from './cores'
import { FilaDeOcorrencias } from './FilaDeOcorrencias'
import { IndiceDosBairros } from './IndiceDosBairros'
import estilos from './PaginaPrioridade.module.css'

const ATRASO_DOS_CONTROLES_EM_MS = 220
const PESO_MAXIMO_NO_GRAFICO = 70
const PRIMEIRO_NIVEL_DE_ESTABILIDADE = 5
const NIVEIS_DA_ESCALA = 5

function comparacoesPadrao({ julgamentosPadrao }: Criterios): Comparacoes {
  return Object.fromEntries(
    julgamentosPadrao.map(({ primeiro, segundo, valor }) => [
      chaveDoPar(primeiro, segundo),
      opcaoDoValor(valor),
    ]),
  )
}

function julgamentosDe(comparacoes: Comparacoes): Julgamento[] {
  return Object.entries(comparacoes).map(([par, opcao]) => {
    const [primeiro, segundo] = par.split('|') as [ChaveDoCriterio, ChaveDoCriterio]
    return { primeiro, segundo, valor: valorDaOpcao(opcao) }
  })
}

function PesosResultantes({
  prioridade,
  criterios,
}: {
  prioridade: Prioridade
  criterios: Criterios
}) {
  const barras = criterios.criterios
    .map(({ chave, nome }) => ({
      chave,
      rotulo: nome,
      valor: prioridade.pesos[chave] * 100,
      texto: formatarPorcentagem(prioridade.pesos[chave] * 100, 1),
      cor: CORES_DOS_CRITERIOS[chave],
    }))
    .sort((a, b) => b.valor - a.valor)
  const maximo = Math.max(PESO_MAXIMO_NO_GRAFICO, ...barras.map((barra) => barra.valor))

  return (
    <div className={estilos.pesos}>
      <BarrasHorizontais
        dados={barras}
        maximo={maximo}
        larguraDoRotulo={120}
        rotuloDoValor="peso"
        alturaDaLinha={36}
      />
      <KpiCard
        rotulo="Razão de consistência (RC)"
        valor={formatarPorcentagem(prioridade.razaoDeConsistencia * 100, 1)}
        contexto={
          prioridade.coerente
            ? 'julgamentos coerentes (RC até 10%)'
            : 'incoerente: revise as comparações'
        }
        ajuda="Compara a coerência dos julgamentos com a de comparações feitas ao acaso. Se A é maior que B e B maior que C, então A deve ser maior que C. Acima de 10%, os pesos não devem ser usados."
        alerta={!prioridade.coerente}
      />
      {!prioridade.coerente && (
        <Aviso tipo="alerta">
          RC acima de 10%: algum julgamento contradiz os outros. O mapa abaixo usa estes pesos mesmo
          assim, só para você ver o efeito.
        </Aviso>
      )}
    </div>
  )
}

function textoDoFator(fator: number): string {
  return `peso × ${formatarNumero(fator, 2).replace(/0$/, '')}`
}

function CelulaDeEstabilidade({ mantidos }: { mantidos: number }) {
  const classe = Math.min(Math.max(mantidos - PRIMEIRO_NIVEL_DE_ESTABILIDADE, 1), NIVEIS_DA_ESCALA)
  return (
    <span className={estilos.celulaDeEstabilidade} data-nivel={classe}>
      {mantidos} de 10
    </span>
  )
}

function Sensibilidade({ testes }: { testes: readonly TesteDeSensibilidade[] }) {
  const criterios = [...new Set(testes.map((teste) => teste.criterio))]
  const fatores = [...new Set(testes.map((teste) => teste.fator))]
  const pior = testes.reduce<TesteDeSensibilidade | null>(
    (atual, teste) => (!atual || teste.mantidosNoTop < atual.mantidosNoTop ? teste : atual),
    null,
  )
  const achar = (criterio: string, fator: number) =>
    testes.find((teste) => teste.criterio === criterio && teste.fator === fator)

  return (
    <Cartao
      titulo="Quantos dos 10 primeiros continuam no top 10"
      ajuda="Cada célula muda o peso de um critério, redistribui o resto e conta quantos dos 10 primeiros continuam no top 10. Mais escuro, mais estável."
      leitura={
        pior &&
        `Com os pesos atuais, o caso mais sensível é ${pior.criterio} ${textoDoFator(pior.fator)}, que mantém ${pior.mantidosNoTop} de 10. Se quase tudo fica acima de 7, o ranking é estável.`
      }
      nota="AHP não é aprendizado de máquina: ele torna explícito e auditável um critério que hoje é implícito."
    >
      <Tabela
        legenda="Sensibilidade do ranking aos pesos"
        colunas={[
          { titulo: 'Critério', valor: (criterio: string) => criterio },
          ...fatores.map((fator) => ({
            titulo: textoDoFator(fator),
            numerica: true,
            valor: (criterio: string) => (
              <CelulaDeEstabilidade mantidos={achar(criterio, fator)?.mantidosNoTop ?? 0} />
            ),
          })),
        ]}
        linhas={criterios}
        chave={(criterio) => criterio}
      />
    </Cartao>
  )
}

function ConteudoDaPrioridade({ criterios }: { criterios: Criterios }) {
  const padrao = useMemo(() => comparacoesPadrao(criterios), [criterios])
  const [comparacoes, definirComparacoes] = useState<Comparacoes>(padrao)
  const atrasadas = useValorAtrasado(comparacoes, ATRASO_DOS_CONTROLES_EM_MS)
  const julgamentos = useMemo(() => julgamentosDe(atrasadas), [atrasadas])
  const consulta = usePrioridade(julgamentos)
  const pares = criterios.julgamentosPadrao.map(
    ({ primeiro, segundo }) => [primeiro, segundo] as const,
  )

  const abaDoIndice = (
    <>
      <Colunas>
        <Cartao
          titulo="Compare os critérios dois a dois"
          ajuda="Para cada par, arraste para o critério que pesa mais. Escala de Saaty: 1 = igual, 3 = moderadamente, 5 = fortemente, 7 = muito, 9 = extremamente."
        >
          <ComparacoesDosCriterios
            criterios={criterios.criterios}
            pares={pares}
            comparacoes={comparacoes}
            aoMudar={(par, opcao) => definirComparacoes((atuais) => ({ ...atuais, [par]: opcao }))}
            aoRestaurar={() => definirComparacoes(padrao)}
          />
        </Cartao>
        <Cartao
          titulo="Pesos resultantes"
          ajuda="Quanto cada critério vale no índice, calculado pelo AHP a partir das comparações ao lado."
        >
          <EstadoDaConsulta consulta={consulta}>
            {(prioridade) => <PesosResultantes prioridade={prioridade} criterios={criterios} />}
          </EstadoDaConsulta>
        </Cartao>
      </Colunas>
      <Secao
        titulo="Onde agir primeiro"
        ajuda="O índice de prioridade de cada bairro, de 0 a 10, com os pesos acima."
      >
        <EstadoDaConsulta consulta={consulta}>
          {(prioridade) => (
            <IndiceDosBairros prioridade={prioridade} criterios={criterios.criterios} />
          )}
        </EstadoDaConsulta>
      </Secao>
    </>
  )
  const abaDoMetodo = (
    <>
      <Cartao
        titulo="Os quatro critérios e como cada um é medido"
        leitura="Cada bairro recebe, em cada critério, a sua posição relativa entre os bairros com 1.000 moradores ou mais (0 = menor valor, 1 = maior). O índice é a soma ponderada dessas posições, uma nota de 0 a 10. Usar a posição evita que poucos bairros extremos achatem os outros."
      >
        <Tabela
          legenda="Critérios do índice"
          colunas={[
            { titulo: 'Critério', valor: (item) => item.nome },
            { titulo: 'Indicador', valor: (item) => item.unidade },
            { titulo: 'O que mede e por quê', valor: (item) => item.descricao },
          ]}
          linhas={criterios.criterios}
          chave={(item) => item.chave}
        />
      </Cartao>
      <Secao
        titulo="O resultado depende muito dos pesos?"
        ajuda="Testa se o ranking muda quando o peso de um critério sobe ou desce."
      >
        <EstadoDaConsulta consulta={consulta}>
          {(prioridade) => <Sensibilidade testes={prioridade.sensibilidade} />}
        </EstadoDaConsulta>
      </Secao>
    </>
  )

  return (
    <Abas
      legenda="Partes do índice de prioridade"
      abas={[
        { chave: 'indice', rotulo: 'Índice dos bairros', conteudo: abaDoIndice },
        {
          chave: 'ocorrencias',
          rotulo: 'Ocorrências classificadas',
          conteudo: <FilaDeOcorrencias julgamentos={julgamentos} criterios={criterios.criterios} />,
        },
        { chave: 'metodo', rotulo: 'Método e sensibilidade', conteudo: abaDoMetodo },
      ]}
    />
  )
}

export function PaginaPrioridade() {
  const consulta = useCriterios()

  return (
    <>
      <CabecalhoDaTela
        titulo="Prioridade (AHP)"
        fontes={['156_EMLURB', 'DEFESA_CIVIL', 'CAMARA_REQUERIMENTOS', 'OUVIDORIA']}
        notas={[
          'Período fixo em 2021 a 2025 (estoque aberto: dois arquivos mais recentes), como na EDA.',
          'RPA e bairro destacam o mapa e filtram a lista; a posição é sempre na cidade toda. A categoria vale só para as ocorrências.',
          'Quem decide compara os critérios dois a dois, e o método calcula os pesos e confere se os julgamentos são coerentes.',
        ]}
      >
        Onde agir primeiro, com critérios explícitos e ajustáveis.
      </CabecalhoDaTela>
      <div className={estilos.aviso}>
        <Aviso tipo="info">
          Os julgamentos carregados são uma proposta do grupo para discussão, não pesos validados
          pela Prefeitura.
        </Aviso>
      </div>
      <EstadoDaConsulta consulta={consulta}>
        {(criterios) => <ConteudoDaPrioridade criterios={criterios} />}
      </EstadoDaConsulta>
    </>
  )
}
