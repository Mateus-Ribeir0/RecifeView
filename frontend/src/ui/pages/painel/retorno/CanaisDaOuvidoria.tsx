import { useOuvidoria } from '../../../../application/consultas/usePainel'
import { useFiltrosGlobais } from '../../../../application/filtros/contexto'
import { formatarNumero, formatarPeriodo, formatarPorcentagem } from '../../../../domain/formatacao'
import type { CanalPorAno } from '../../../../domain/painel'
import { BarrasEmpilhadas } from '../../../charts/BarrasEmpilhadas'
import { COR } from '../../../charts/estilo'
import { Cartao } from '../../../components/Cartao'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { KpiCard } from '../../../components/KpiCard'
import { Medidor } from '../../../components/Medidor'
import { Colunas, Secao } from '../../../components/Secao'
import estilos from './PaginaRetorno.module.css'

const SEGMENTOS = [
  { chave: '0800', rotulo: '0800 (telefone)', cor: COR.claro },
  { chave: 'SITE', rotulo: 'site', cor: COR.medio },
  { chave: 'E-MAIL', rotulo: 'e-mail', cor: COR.principal },
  { chave: 'ATENDIMENTO PESSOAL', rotulo: 'presencial', cor: COR.marinho },
  { chave: 'APP CONECTA RECIFE', rotulo: 'app Conecta Recife', cor: 'var(--cor-fonte-camara)' },
  { chave: 'OUTROS', rotulo: 'outros', cor: COR.contexto },
]

function linhasPorAno(canais: readonly CanalPorAno[]) {
  const anos = [...new Set(canais.map((canal) => canal.ano))].sort((a, b) => a - b)
  return anos.map((ano) => {
    const linha: Record<string, number | string> = { ano: String(ano) }
    canais
      .filter((canal) => canal.ano === ano)
      .forEach((canal) => {
        linha[canal.canal] = canal.pct
      })
    return linha
  })
}

export function CanaisDaOuvidoria() {
  const { filtros } = useFiltrosGlobais()
  const consulta = useOuvidoria(filtros)
  const periodo = formatarPeriodo(filtros.anoInicio, filtros.anoFim)

  return (
    <Secao
      titulo="Ouvidoria: por onde a manifestação entra"
      ajuda="Por quais canais as manifestações chegam à Ouvidoria a cada ano."
    >
      <EstadoDaConsulta
        consulta={consulta}
        estaVazia={({ dados }) => dados.canais.length === 0}
        mensagemDeVazio="A Ouvidoria publica o canal de entrada de 2018 a 2024. Ajuste o período para ver este bloco."
      >
        {({ dados, meta }) => (
          <Colunas proporcao="larga">
            <Cartao
              titulo="O telefone domina, e o app mal aparece"
              leitura="O telefone virou o canal dominante, e o app só aparece em 2023, com cerca de 3%. O problema não é falta de canal digital para o cidadão: é o que acontece depois que o pedido entra."
              nota={`Fonte: Ouvidoria. Período: ${periodo}. n = ${formatarNumero(meta.n)}. Filtros de território e categoria não se aplicam.`}
            >
              <BarrasEmpilhadas
                dados={linhasPorAno(dados.canais)}
                eixo="ano"
                segmentos={SEGMENTOS}
                orientacao="vertical"
                emPercentual
                formatar={(valor) => formatarPorcentagem(valor, 1)}
              />
            </Cartao>
            <div className={estilos.pilha}>
              <KpiCard
                rotulo="App Conecta Recife na Ouvidoria"
                valor={formatarPorcentagem(dados.pctDoApp, 1)}
                contexto={dados.anoDoApp ? `em ${dados.anoDoApp}` : undefined}
                visual={
                  <Medidor
                    porcentagem={dados.pctDoApp ?? 0}
                    rotulo="Parte das manifestações que entram pelo app"
                  />
                }
              />
              <KpiCard
                rotulo="Respondidas no prazo"
                valor={formatarPorcentagem(dados.pctNoPrazo)}
                contexto="Ouvidoria, no período"
                visual={
                  <Medidor
                    porcentagem={dados.pctNoPrazo ?? 0}
                    rotulo="Parte das manifestações respondidas no prazo"
                  />
                }
              />
            </div>
          </Colunas>
        )}
      </EstadoDaConsulta>
    </Secao>
  )
}
