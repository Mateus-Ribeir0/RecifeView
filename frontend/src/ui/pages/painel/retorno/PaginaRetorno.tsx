import { useState } from 'react'

import { useRetorno } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import {
  formatarDias,
  formatarNumero,
  formatarPeriodo,
  formatarPorcentagem,
} from '../../../../domain/formatacao'
import { nomeDaCategoria, nomeDoOrgao } from '../../../../domain/nomes'
import type { Retorno } from '../../../../domain/painel'
import { BarrasHorizontais } from '../../../charts/BarrasHorizontais'
import { BarrasVerticais } from '../../../charts/BarrasVerticais'
import { COR } from '../../../charts/estilo'
import { MapaDeCalor } from '../../../charts/MapaDeCalor'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../../components/GradeDeKpis'
import { KpiCard } from '../../../components/KpiCard'
import { Colunas, Secao } from '../../../components/Secao'
import { CaminhoDaCategoria } from './CaminhoDaCategoria'
import { CanaisDaOuvidoria } from './CanaisDaOuvidoria'

const CANAIS_CURTOS: Readonly<Record<string, string>> = {
  OFICIO: 'ofício',
  'PROTOCOLO NA PREFEITURA': 'protocolo',
  'LOTE JSON SISTEMA PCR': 'lote JSON',
  'SISTEMA SEGOV': 'SEGOV',
  'ENVIADO AO EXECUTIVO': 'Executivo',
  'E-MAIL': 'e-mail',
}

function etapasDoFunil({ resumo }: Retorno) {
  const texto = (n: number) =>
    `${formatarNumero(n)} (${formatarPorcentagem((n / Math.max(resumo.total, 1)) * 100)})`
  return [
    {
      chave: 'apresentadas',
      rotulo: 'Apresentadas na Câmara',
      valor: resumo.total,
      texto: texto(resumo.total),
      cor: COR.claro,
    },
    {
      chave: 'enviadas',
      rotulo: 'Enviadas à Prefeitura',
      valor: resumo.enviadas,
      texto: texto(resumo.enviadas),
      cor: COR.principal,
    },
    {
      chave: 'respondidas',
      rotulo: 'Com resposta registrada',
      valor: resumo.respondidas,
      texto: texto(resumo.respondidas),
      cor: COR.marinho,
    },
  ]
}

function colunasDoCanal({ porAno }: Retorno) {
  return porAno.map((item) => ({
    rotulo: `${item.ano}\n${item.canal ? (CANAIS_CURTOS[item.canal] ?? item.canal.toLowerCase()) : 'sem dado'}`,
    valor: item.pctRespondidas,
    texto: formatarPorcentagem(item.pctRespondidas, 1),
    detalhe: 'das indicações com resposta registrada',
  }))
}

function orgaosDoMapa({ celulas }: Retorno) {
  const totais = new Map<string, number>()
  celulas.forEach(({ orgao, n }) => totais.set(orgao, (totais.get(orgao) ?? 0) + n))
  return [...totais.entries()]
    .sort((a, b) => {
      if (a[0] === 'OUTROS') return 1
      if (b[0] === 'OUTROS') return -1
      return b[1] - a[1]
    })
    .map(([orgao]) => ({ chave: orgao, rotulo: nomeDoOrgao(orgao) }))
}

interface ConteudoProps {
  dados: Retorno
  n: number
  periodo: string
}

function ConteudoDoRetorno({ dados, n, periodo }: ConteudoProps) {
  const [escolhida, definirEscolhida] = useState<string | null>(null)
  const foco = escolhida ?? dados.dispersoes[0]?.categoria ?? null
  const dispersao = dados.dispersoes.find((item) => item.categoria === foco)
  const caminho = dados.caminhos.find((item) => item.categoria === foco)
  const nota = `Fonte: Câmara Municipal (SAGL). Período: ${periodo}. n = ${formatarNumero(n)}.`

  return (
    <>
      <GradeDeKpis>
        <KpiCard
          rotulo="Indicações de vereadores"
          valor={formatarNumero(dados.resumo.total)}
          contexto="pedidos à Prefeitura"
          ajuda="Indicações apresentadas na Câmara Municipal no recorte, lidas do sistema público SAGL."
        />
        <KpiCard
          rotulo="Chegam à Prefeitura"
          valor={formatarPorcentagem(dados.resumo.pctEnviadas)}
          contexto={`envio em ${formatarDias(dados.resumo.medianaDiasAteEnvio)}`}
          ajuda="Indicações com envio à Prefeitura registrado na tramitação, e a mediana de dias até o envio."
        />
        <KpiCard
          rotulo="Voltam com resposta"
          valor={formatarPorcentagem(dados.resumo.pctRespondidas)}
          contexto={`${formatarNumero(dados.resumo.respondidas)} indicações`}
          ajuda="Sem resposta registrada não quer dizer que o serviço não foi feito: quer dizer que a informação não voltou."
        />
        <KpiCard
          rotulo="Tempo até a resposta"
          valor={formatarDias(dados.resumo.medianaDiasAteResposta)}
          contexto="mediana"
          ajuda="Mediana dos dias entre a apresentação e a resposta registrada, só para as que têm resposta."
        />
      </GradeDeKpis>
      <Secao
        titulo="A perda está toda depois da entrada"
        ajuda="Onde o pedido do vereador se perde: entra, vai para a Prefeitura e raramente volta com resposta."
      >
        <Colunas>
          <Cartao
            titulo="Funil das indicações"
            leitura="Quase tudo sai da Câmara em poucos dias. A queda acontece dentro da Prefeitura, no caminho de volta."
            nota={nota}
          >
            <BarrasHorizontais
              dados={etapasDoFunil(dados)}
              maximo={dados.resumo.total * 1.3}
              larguraDoRotulo={170}
              rotuloDoValor="indicações"
              alturaDaLinha={48}
            />
          </Cartao>
          <Cartao
            titulo="Quando o envio vira sistema, a resposta aparece"
            ajuda="% das indicações com resposta registrada por ano, com o canal de envio mais usado em cada ano."
            leitura="De ofício e protocolo em papel para lote e sistema da SEGOV, a parte com resposta registrada sobe de menos de 1% para cerca de 45%. Anos recentes ainda podem receber resposta."
            nota={nota}
          >
            <BarrasVerticais
              dados={colunasDoCanal(dados)}
              rotuloDoEixo="% com resposta registrada"
              maximo={60}
              altura={260}
            />
          </Cartao>
        </Colunas>
      </Secao>
      <Secao
        titulo="O mesmo tipo de pedido vai para órgãos diferentes"
        ajuda="Para onde vão as indicações de cada categoria. Clique numa linha para ver o caminho dela."
      >
        <Colunas proporcao="larga">
          <Cartao
            titulo="Destino por categoria (% de cada linha)"
            leitura="Cada linha soma 100%. Clique numa linha para ver o caminho dela até o desfecho. Categoria e órgão vêm da ementa (rótulo fraco)."
            nota={nota}
          >
            <MapaDeCalor
              linhas={dados.dispersoes.map(({ categoria }) => ({
                chave: categoria,
                rotulo: nomeDaCategoria(categoria),
              }))}
              colunas={orgaosDoMapa(dados)}
              celulas={dados.celulas.map(({ categoria, orgao, pct, n: quantidade }) => ({
                linha: categoria,
                coluna: orgao,
                pct,
                n: quantidade,
              }))}
              selecionada={escolhida}
              aoSelecionar={definirEscolhida}
            />
          </Cartao>
          <Cartao
            titulo={`${nomeDaCategoria(foco)}: órgão e desfecho`}
            leitura={
              dispersao &&
              `${nomeDaCategoria(foco)} vai para ${dispersao.orgaos} órgãos; o principal (${nomeDoOrgao(dispersao.orgaoPrincipal)}) recebe ${formatarPorcentagem(dispersao.pctPrincipal)}.`
            }
          >
            {caminho && <CaminhoDaCategoria caminho={caminho} />}
          </Cartao>
        </Colunas>
      </Secao>
    </>
  )
}

export function PaginaRetorno() {
  const { filtros } = useFiltrosGlobais()
  const consulta = useRetorno(filtros)

  return (
    <>
      <CabecalhoDaTela
        titulo="Retorno e fragmentação"
        fontes={['CAMARA_REQUERIMENTOS', 'OUVIDORIA']}
        ignorados={[
          'Ouvidoria: não tem bairro nem a mesma classificação de serviço; o último bloco segue só o período.',
        ]}
        atualizando={consulta.atualizando}
      >
        Depois que a demanda entra, ela muda de mão entre órgãos e raramente volta com resposta
        registrada. A Câmara é a única fonte pública que mostra o caminho inteiro, do pedido do
        vereador até a resposta da Prefeitura.
      </CabecalhoDaTela>
      <EstadoDaConsulta
        consulta={consulta}
        estaVazia={({ dados }) => dados.resumo.total === 0}
        mensagemDeVazio="Nenhuma indicação da Câmara para estes filtros. A Câmara cobre 2021 a 2025 e só as categorias de serviço urbano citadas nas ementas."
      >
        {({ dados, meta }) => (
          <ConteudoDoRetorno
            dados={dados}
            n={meta.n}
            periodo={formatarPeriodo(filtros.anoInicio, filtros.anoFim)}
          />
        )}
      </EstadoDaConsulta>
      <CanaisDaOuvidoria />
    </>
  )
}
