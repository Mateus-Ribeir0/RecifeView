import { nomeDaCategoria, nomeDoOrgao } from '../../../../domain/nomes'
import type { CaminhoDaCategoria as Caminho } from '../../../../domain/painel'
import { COR } from '../../../charts/estilo'
import { GraficoDeFluxo, type LigacaoDoFluxo, type NoDoFluxo } from '../../../charts/GraficoDeFluxo'

const ORDEM_DOS_DESFECHOS = ['com resposta', 'sem resposta', 'sem envio', 'retirada']
const CORES_DOS_DESFECHOS: Readonly<Record<string, string>> = {
  'com resposta': COR.marinho,
  'sem resposta': COR.claro,
  'sem envio': COR.contexto,
  retirada: COR.contexto,
}

function montarFluxo(caminho: Caminho): { nos: NoDoFluxo[]; ligacoes: LigacaoDoFluxo[] } {
  const totais = new Map<string, number>()
  caminho.fluxos.forEach(({ orgao, n }) => totais.set(orgao, (totais.get(orgao) ?? 0) + n))
  const orgaos = [...totais.entries()].sort((a, b) => b[1] - a[1]).map(([orgao]) => orgao)
  const presentes = new Set(caminho.fluxos.map((fluxo) => fluxo.desfecho))
  const desfechos = ORDEM_DOS_DESFECHOS.filter((desfecho) => presentes.has(desfecho))
  const nos: NoDoFluxo[] = [
    { name: nomeDaCategoria(caminho.categoria), cor: COR.principal },
    ...orgaos.map((orgao) => ({ name: nomeDoOrgao(orgao), cor: COR.medio })),
    ...desfechos.map((desfecho) => ({
      name: desfecho,
      cor: CORES_DOS_DESFECHOS[desfecho] ?? COR.contexto,
    })),
  ]
  const posicaoDoOrgao = (orgao: string) => orgaos.indexOf(orgao) + 1
  const posicaoDoDesfecho = (desfecho: string) => desfechos.indexOf(desfecho) + orgaos.length + 1
  return {
    nos,
    ligacoes: [
      ...orgaos.map((orgao) => ({
        source: 0,
        target: posicaoDoOrgao(orgao),
        value: totais.get(orgao) ?? 0,
      })),
      ...caminho.fluxos.map((fluxo) => ({
        source: posicaoDoOrgao(fluxo.orgao),
        target: posicaoDoDesfecho(fluxo.desfecho),
        value: fluxo.n,
      })),
    ],
  }
}

export function CaminhoDaCategoria({ caminho }: { caminho: Caminho }) {
  const { nos, ligacoes } = montarFluxo(caminho)
  return <GraficoDeFluxo nos={nos} ligacoes={ligacoes} />
}
