import { useSobreOsDados } from '../../../../application/consultas/usePainel'
import { formatarDataEHora, formatarNumero } from '../../../../domain/formatacao'
import { ROTULOS_DAS_CORRECOES } from '../../../../domain/importacoes'
import { nomeDaFonte, ORDEM_DAS_FONTES } from '../../../../domain/fontes'
import type { SobreOsDados } from '../../../../domain/painel'
import { MapaDeCobertura } from '../../../charts/MapaDeCobertura'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { Secao } from '../../../components/Secao'
import { Tabela, type ColunaDaTabela } from '../../../components/Tabela'
import estilos from './PaginaSobreOsDados.module.css'

interface FonteDescrita {
  fonte: string
  periodo: string
  umaLinha: string
  origem: string
}

const FONTES: readonly FonteDescrita[] = [
  {
    fonte: 'Central 156 / Emlurb',
    periodo: '2012 a 2026',
    umaLinha: 'solicitação de serviço urbano',
    origem: 'Portal de Dados Abertos do Recife (ODbL)',
  },
  {
    fonte: 'Defesa Civil',
    periodo: '2014 a 2024',
    umaLinha: 'ação (vistoria, lona, monitoramento), não pedido',
    origem: 'Portal de Dados Abertos do Recife',
  },
  {
    fonte: 'Ouvidoria-Geral',
    periodo: '2018 a 2025',
    umaLinha: 'manifestação (reclamação, denúncia, pedido)',
    origem: 'Portal de Dados Abertos do Recife',
  },
  {
    fonte: 'SEDEC (áreas de risco)',
    periodo: '2012 a 2024',
    umaLinha: 'chamado em área de risco',
    origem: 'cópia de 09/03/2024 no Internet Archive',
  },
  {
    fonte: 'Câmara Municipal',
    periodo: '2021 a 2025',
    umaLinha: 'indicação ou requerimento de vereador',
    origem: 'sistema público SAGL da Câmara',
  },
  {
    fonte: 'IBGE, Censo 2022',
    periodo: '2022',
    umaLinha: 'população, domicílios e % em favela de 94 bairros',
    origem: 'SIDRA, tabelas 9922, 9923 e 10206',
  },
]

const COLUNAS_DAS_FONTES: readonly ColunaDaTabela<FonteDescrita>[] = [
  { titulo: 'Fonte', valor: (item) => item.fonte },
  { titulo: 'Período', valor: (item) => item.periodo },
  { titulo: 'Uma linha é', valor: (item) => item.umaLinha },
  { titulo: 'Origem', valor: (item) => item.origem },
]

const CUIDADOS: readonly [string, string][] = [
  [
    'Não há chave comum entre as fontes.',
    'O mesmo problema registrado no 156 e na Ouvidoria vira duas linhas que não se ligam; o cruzamento é por bairro, serviço e período.',
  ],
  [
    'Mais pedido não é mais problema.',
    'O painel mostra taxa por habitante ao lado do volume e trata bairros com menos de 1.000 moradores à parte.',
  ],
  ['Defesa Civil conta ações.', 'O painel usa só as ações pedidas pelo cidadão.'],
  [
    'Câmara:',
    'categoria e órgão vêm de palavras-chave na ementa (rótulo fraco); sem resposta registrada não quer dizer que o serviço não foi feito.',
  ],
  [
    'Prazos:',
    'só pedidos atendidos têm tempo final. Prazo zero costuma ser encerramento administrativo. Anos recentes têm cauda incompleta.',
  ],
  [
    'Estoque aberto:',
    'só os dois arquivos anuais mais recentes do 156, porque cada arquivo é um retrato e pedidos antigos podem ter congelado nele.',
  ],
  [
    'Coordenadas não são usadas:',
    'faltam em boa parte do 156, e não ao acaso; o recorte territorial é o bairro oficial (94 bairros) e a RPA.',
  ],
]

const GLOSSARIO: readonly [string, string][] = [
  ['RPA', 'Região Político-Administrativa: as 6 regiões em que a Prefeitura divide os 94 bairros.'],
  ['Mediana', 'O valor do meio: metade dos pedidos leva menos que isso.'],
  ['p90', '90% dos pedidos levam menos que isso; 1 em cada 10 leva mais.'],
  ['Local repetido', 'Pedido cujo endereço e serviço aparecem 2 ou mais vezes (156, 2015 a 2025).'],
  ['Duplicidade', 'Repetição em até 7 dias: provável pedido em dobro.'],
  ['Reincidência', 'Repetição 30 dias ou mais depois: o problema voltou.'],
  ['Indicação', 'Pedido de providência que um vereador envia à Prefeitura.'],
  [
    'AHP',
    'Método que transforma comparações par a par entre critérios em pesos, com teste de coerência.',
  ],
]

function ConteudoDoSobre({ dados }: { dados: SobreOsDados }) {
  return (
    <>
      <Secao
        titulo="Cobertura: registros por fonte e ano"
        ajuda="Célula vazia: a fonte não publica aquele ano."
      >
        <Cartao
          titulo="Quantos registros cada fonte tem em cada ano"
          nota="Células vazias: a fonte não publica aquele ano. 2025 e 2026 são parciais: a Ouvidoria de 2025 só traz parte do ano, o arquivo de 2025 da Defesa Civil foi publicado vazio e 2026 vai até a data do retrato."
        >
          <MapaDeCobertura
            fontes={ORDEM_DAS_FONTES.map((fonte) => ({ chave: fonte, rotulo: nomeDaFonte(fonte) }))}
            celulas={dados.cobertura}
          />
        </Cartao>
      </Secao>
      <Secao
        titulo="O que foi corrigido antes de agregar"
        ajuda="Ajustes aplicados aos dados, com quantos registros cada um afetou."
      >
        <Cartao
          titulo={`${formatarNumero(dados.registrosNaBase)} registros na base`}
          nota={`As correções da EDA (N3), somadas em todas as importações. Última atualização: ${formatarDataEHora(dados.atualizadoEm)}.`}
        >
          <Tabela
            legenda="Correções aplicadas"
            colunas={[
              {
                titulo: 'Correção',
                valor: (item) => ROTULOS_DAS_CORRECOES[item.correcao] ?? item.correcao,
              },
              {
                titulo: 'Registros',
                numerica: true,
                valor: (item) => formatarNumero(item.registros),
              },
            ]}
            linhas={dados.correcoes}
            chave={(item) => item.correcao}
          />
        </Cartao>
      </Secao>
    </>
  )
}

export function PaginaSobreOsDados() {
  const consulta = useSobreOsDados()

  return (
    <>
      <CabecalhoDaTela titulo="Sobre os dados" semRecorte>
        O painel lê a base do RecifeView: registros de cinco portas de entrada, de 2012 a 2026, só
        do município do Recife, com as correções da EDA (N3).
      </CabecalhoDaTela>
      <Secao titulo="Fontes" ajuda="As cinco portas de entrada e o que cada registro representa.">
        <Tabela
          legenda="Fontes do painel"
          colunas={COLUNAS_DAS_FONTES}
          linhas={FONTES}
          chave={(item) => item.fonte}
        />
      </Secao>
      <EstadoDaConsulta consulta={consulta}>
        {(dados) => <ConteudoDoSobre dados={dados} />}
      </EstadoDaConsulta>
      <Secao titulo="Cuidados de leitura" ajuda="O que pode enganar na leitura dos números.">
        <ul className={estilos.lista}>
          {CUIDADOS.map(([termo, texto]) => (
            <li key={termo}>
              <strong>{termo}</strong> {texto}
            </li>
          ))}
        </ul>
      </Secao>
      <Secao titulo="Privacidade" ajuda="O que nunca aparece no painel e por quê.">
        <p className={estilos.texto}>
          O painel só mostra contagens, indicadores e campos que as fontes já publicam. Não saem da
          base: o texto livre da SEDEC, as ementas, o pseudônimo de endereço (id_local), as
          coordenadas e a autoria das indicações. A lista de pontos crônicos mostra bairro e
          serviço, nunca o endereço. Na importação, colunas com dado pessoal são descartadas.
        </p>
      </Secao>
      <Secao titulo="Glossário" ajuda="Termos usados no painel, em uma linha.">
        <dl className={estilos.glossario}>
          {GLOSSARIO.map(([termo, significado]) => (
            <div key={termo}>
              <dt>{termo}</dt>
              <dd>{significado}</dd>
            </div>
          ))}
        </dl>
      </Secao>
    </>
  )
}
