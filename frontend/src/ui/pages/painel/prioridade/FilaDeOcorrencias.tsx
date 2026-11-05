import { useMemo, useState } from 'react'

import { useCatalogo, useFila } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import { temTerritorio } from '../../../../domain/filtros'
import { formatarNumero, formatarPorcentagem } from '../../../../domain/formatacao'
import {
  CHAVES_DOS_CRITERIOS,
  NOTA_ALTA,
  NOTA_MAXIMA,
  type Criterio,
  type FilaClassificada,
  type FonteDaFila,
  type Julgamento,
  type OcorrenciaClassificada,
} from '../../../../domain/prioridade'
import { Histograma } from '../../../charts/Histograma'
import { Legenda } from '../../../charts/Legenda'
import { Botao } from '../../../components/Botao'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { KpiCard } from '../../../components/KpiCard'
import { Colunas } from '../../../components/Secao'
import { Tabela, type ColunaDaTabela } from '../../../components/Tabela'
import { CORES_DOS_CRITERIOS } from './cores'
import estilos from './PaginaPrioridade.module.css'
import { textosDaOcorrencia } from './textosDaOcorrencia'

const SEMENTE_INICIAL = 2026
const LIMITE_DA_SEMENTE = 1_000_000

interface OpcaoDeFonte {
  fonte: FonteDaFila
  nome: string
  registro: string
  explica: string
}

const OPCOES_DE_FONTE: readonly OpcaoDeFonte[] = [
  {
    fonte: '156',
    nome: 'Central 156 / Emlurb',
    registro: 'pedidos abertos',
    explica:
      'pedidos abertos do 156: risco e vulnerabilidade vêm do bairro do pedido; atraso e reincidência vêm do próprio pedido.',
  },
  {
    fonte: 'camara',
    nome: 'Indicações da Câmara',
    registro: 'indicações sem resposta',
    explica:
      'indicações de vereadores enviadas à Prefeitura e ainda sem resposta registrada: risco e vulnerabilidade vêm do bairro; o atraso conta desde o envio; a reincidência são outras indicações do mesmo tema no mesmo bairro nos 90 dias anteriores.',
  },
  {
    fonte: 'ouvidoria',
    nome: 'Ouvidoria',
    registro: 'manifestações abertas',
    explica:
      'manifestações abertas na Ouvidoria. A base aberta não tem bairro, endereço nem coordenadas, então a nota usa só o atraso em relação ao prazo legal e não é comparável com a das outras fontes.',
  },
]

const LEITURAS: Readonly<Record<FonteDaFila, string>> = {
  '156':
    'Atraso: 5 = o pedido chegou ao prazo típico da categoria; 10 = o dobro do prazo ou mais. Reincidência: 0 = primeiro pedido do serviço no endereço; 10 = dez ou mais pedidos anteriores (escala log).',
  camara:
    'Atraso: 5 = a indicação chegou ao tempo típico de resposta do tema; 10 = o dobro ou mais. Sem resposta registrada pode incluir resposta dada fora do sistema da Câmara; tema e bairro vêm da ementa (rótulo fraco).',
  ouvidoria:
    'Atraso: todas as manifestações abertas já passaram do prazo legal, então a nota é a posição de cada uma entre as abertas pelos dias além do prazo: 10 = a mais atrasada.',
}

function BarraDeContribuicao({ item }: { item: OcorrenciaClassificada }) {
  return (
    <div className={estilos.contribuicao} aria-hidden="true">
      {CHAVES_DOS_CRITERIOS.map((chave) => (
        <span
          key={chave}
          style={{
            width: `${(item.contribuicoes[chave] / NOTA_MAXIMA) * 100}%`,
            background: CORES_DOS_CRITERIOS[chave],
          }}
          title={`${chave}: ${formatarNumero(item.contribuicoes[chave], 1)} pontos`}
        />
      ))}
    </div>
  )
}

interface CartaoProps {
  item: OcorrenciaClassificada
  fonte: FonteDaFila
  total: number
  nomeDoBairro: string
}

function CartaoDeOcorrencia({ item, fonte, total, nomeDoBairro }: CartaoProps) {
  const textos = textosDaOcorrencia(item, fonte, nomeDoBairro)
  return (
    <article className={estilos.ocorrencia}>
      <div>
        <p className={estilos.legendaDaNota}>nota</p>
        <p className={`${estilos.nota} numero`}>
          {formatarNumero(item.indice, 1)} <small>de 10</small>
        </p>
        <p className={estilos.legendaDaNota}>
          {formatarNumero(item.fila)}º de {formatarNumero(total)} na fila
        </p>
      </div>
      <div className={estilos.textoDaOcorrencia}>
        <h4>{textos.titulo}</h4>
        <p>{textos.contexto}</p>
        <p>{textos.tempo}</p>
        <p>{textos.repeticao}</p>
        <BarraDeContribuicao item={item} />
      </div>
    </article>
  )
}

function colunasDoTopo(
  fonte: FonteDaFila,
  nomes: ReadonlyMap<string, string>,
): ColunaDaTabela<OcorrenciaClassificada>[] {
  return [
    {
      titulo: 'Fila',
      numerica: true,
      ajuda: 'Posição na fila: 1º é o de maior nota entre os abertos.',
      valor: (item) => `${formatarNumero(item.fila)}º`,
    },
    {
      titulo: 'Nota',
      numerica: true,
      ajuda: 'Nota de prioridade de 0 a 10 pelo AHP.',
      valor: (item) => formatarNumero(item.indice, 1),
    },
    {
      titulo: 'Registro',
      valor: (item) =>
        textosDaOcorrencia(item, fonte, nomes.get(item.bairroOficial ?? '') ?? '').titulo,
    },
    {
      titulo: fonte === 'ouvidoria' ? 'Órgão' : 'Bairro',
      valor: (item) =>
        fonte === 'ouvidoria'
          ? (item.orgao ?? 'não informado')
          : (nomes.get(item.bairroOficial ?? '') ?? 'não informado'),
    },
    {
      titulo: 'Idade',
      numerica: true,
      valor: (item) => `${formatarNumero(item.idadeDias)} dias`,
    },
  ]
}

interface ResultadoProps {
  fila: FilaClassificada
  opcao: OpcaoDeFonte
  aoSortear: () => void
  criterios: readonly Criterio[]
}

function ResultadoDaFila({ fila, opcao, aoSortear, criterios }: ResultadoProps) {
  const { dados: catalogo } = useCatalogo()
  const nomes = useMemo(
    () => new Map(catalogo?.bairros.map((bairro) => [bairro.bairroOficial, bairro.nome])),
    [catalogo],
  )
  const [aba, definirAba] = useState<'cartoes' | 'tabela'>('cartoes')
  const nomeDe = (item: OcorrenciaClassificada) => nomes.get(item.bairroOficial ?? '') ?? ''
  const legenda = criterios.map(({ chave, nome }) => ({
    chave,
    rotulo: nome,
    cor: CORES_DOS_CRITERIOS[chave],
  }))

  return (
    <>
      <div className={estilos.sorteio}>
        <Botao variante="secundario" compacto onClick={aoSortear}>
          Sortear ocorrências
        </Botao>
        <p>
          Três registros sorteados entre os {formatarNumero(fila.classificados)} {opcao.registro},
          da maior nota para a menor. A fila é a ordem de todos eles pela nota.
        </p>
      </div>
      <div role="tablist" aria-label="Forma de ver os registros" className={estilos.abas}>
        <button
          type="button"
          role="tab"
          aria-selected={aba === 'cartoes'}
          onClick={() => definirAba('cartoes')}
        >
          Cartões
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={aba === 'tabela'}
          onClick={() => definirAba('tabela')}
        >
          Tabela
        </button>
      </div>
      {aba === 'tabela' ? (
        <Tabela
          legenda="Registros sorteados"
          colunas={colunasDoTopo(fila.fonte, nomes)}
          linhas={fila.amostra}
          chave={(item) => String(item.fila)}
        />
      ) : (
        <Colunas proporcao="larga">
          <div className={estilos.ocorrencias}>
            <Legenda itens={legenda} />
            {fila.amostra.map((item, indice) => (
              <CartaoDeOcorrencia
                key={`${item.fila}-${indice}`}
                item={item}
                fonte={fila.fonte}
                total={fila.classificados}
                nomeDoBairro={nomeDe(item)}
              />
            ))}
          </div>
          <div className={estilos.ocorrencias}>
            <Cartao
              titulo="Onde cada um cai na fila"
              ajuda="Quantos registros em aberto há em cada faixa de nota. Os traços são os sorteados."
            >
              <Histograma
                faixas={fila.distribuicao}
                marcas={fila.amostra.map((item, indice) => ({
                  rotulo: `${indice + 1}º`,
                  valor: item.indice,
                }))}
                rotuloDoEixo={opcao.registro}
              />
            </Cartao>
            <KpiCard
              rotulo={`Com nota ${NOTA_ALTA} ou mais`}
              valor={formatarPorcentagem(fila.pctNotaAlta, 1)}
              contexto={`${formatarNumero(fila.comNotaAlta)} de ${formatarNumero(fila.classificados)} ${opcao.registro}`}
              ajuda="Com os pesos atuais. Seria o primeiro lote de uma fila de atendimento."
            />
          </div>
        </Colunas>
      )}
      <p className={estilos.leitura}>
        {LEITURAS[fila.fonte]} É um exemplo: os tetos e os pesos precisam ser validados com quem
        opera cada serviço.
      </p>
      <details className={estilos.detalhes}>
        <summary>A fila inteira: os 20 de maior nota</summary>
        <Tabela
          legenda="Os 20 registros de maior nota"
          colunas={colunasDoTopo(fila.fonte, nomes)}
          linhas={fila.topo}
          chave={(item, indice) => `${item.fila}-${indice}`}
        />
      </details>
    </>
  )
}

interface Propriedades {
  julgamentos: readonly Julgamento[]
  criterios: readonly Criterio[]
}

export function FilaDeOcorrencias({ julgamentos, criterios }: Propriedades) {
  const { filtros } = useFiltrosGlobais()
  const [fonte, definirFonte] = useState<FonteDaFila>('156')
  const [semente, definirSemente] = useState(SEMENTE_INICIAL)
  const parametros = useMemo(
    () => ({ fonte, julgamentos, semente, filtros }),
    [fonte, julgamentos, semente, filtros],
  )
  const consulta = useFila(parametros)
  const opcao = OPCOES_DE_FONTE.find((item) => item.fonte === fonte) ?? OPCOES_DE_FONTE[0]
  if (!opcao) return null
  const naoSeAplica =
    fonte === 'ouvidoria' && (temTerritorio(filtros) || filtros.categorias.length > 0)

  return (
    <div className={estilos.fila}>
      <fieldset className={estilos.fontes}>
        <legend className="visualmente-oculto">Fonte dos registros</legend>
        {OPCOES_DE_FONTE.map((item) => (
          <label key={item.fonte}>
            <input
              type="radio"
              name="fonte-da-fila"
              checked={fonte === item.fonte}
              onChange={() => definirFonte(item.fonte)}
            />
            {item.nome}
          </label>
        ))}
      </fieldset>
      <p className={estilos.leitura}>
        O índice acima é do bairro. Aqui o mesmo AHP, com os mesmos pesos, dá uma nota de 0 a 10 a{' '}
        {opcao.explica}
      </p>
      {naoSeAplica && (
        <p className={estilos.leitura}>
          Os filtros de território e de categoria não valem aqui: a Ouvidoria não tem bairro nem a
          mesma classificação de serviço.
        </p>
      )}
      <EstadoDaConsulta
        consulta={consulta}
        estaVazia={(dados) => dados.classificados === 0}
        mensagemDeVazio="Nenhum registro em aberto no recorte escolhido, ou o bairro está fora do índice (menos de 1.000 moradores)."
      >
        {(fila) => (
          <>
            <p className={estilos.leitura}>
              {opcao.nome} tem {formatarNumero(fila.registrosNaBase)} registros na base;{' '}
              {formatarNumero(fila.emAberto)} estão em aberto.
            </p>
            <ResultadoDaFila
              fila={fila}
              opcao={opcao}
              criterios={criterios}
              aoSortear={() => definirSemente(Math.floor(Math.random() * LIMITE_DA_SEMENTE))}
            />
          </>
        )}
      </EstadoDaConsulta>
    </div>
  )
}
