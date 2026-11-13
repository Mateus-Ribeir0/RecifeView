import { useState } from 'react'
import { useNavigate } from 'react-router'

import { useServicoDeContribuicoes } from '../../../application/contribuicoes/contexto'
import { useFilaDeRelatos } from '../../../application/contribuicoes/useFilaDeRelatos'
import { podeGerarPacote, type ResumoDasContribuicoes } from '../../../domain/contribuicoes'
import { contar, formatarNumero } from '../../../domain/formatacao'
import { Abas } from '../../components/Abas'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { ComoFunciona } from './ComoFunciona'
import estilos from './Contribuicoes.module.css'
import { ListaDeOcorrencias } from './ListaDeOcorrencias'
import { PenteFino } from './PenteFino'

function motivoDoBloqueio(resumo: ResumoDasContribuicoes): string {
  if (resumo.aguardandoRevisao > 0) {
    return `Decida ${contar(resumo.aguardandoRevisao, 'dupla', 'duplas')} no pente fino para gerar o pacote.`
  }
  if (resumo.prontasParaPacote === 0) return 'Nenhuma ocorrência nova para o pacote.'
  return `${contar(resumo.prontasParaPacote, 'ocorrência pronta', 'ocorrências prontas')} para o pacote.`
}

function Indicadores({ resumo }: { resumo: ResumoDasContribuicoes }) {
  return (
    <GradeDeKpis>
      <KpiCard
        rotulo="Relatos recebidos"
        valor={formatarNumero(resumo.relatos)}
        contexto={contar(
          resumo.semRetorno,
          'diz que não teve retorno',
          'dizem que não tiveram retorno',
        )}
      />
      <KpiCard
        rotulo="Ocorrências distintas"
        valor={formatarNumero(resumo.ocorrencias)}
        contexto={contar(resumo.somados, 'relato somado', 'relatos somados') + ' sem duplicar'}
      />
      <KpiCard
        rotulo="Aguardando o pente fino"
        valor={formatarNumero(resumo.aguardandoRevisao)}
        contexto="duplas parecidas sem decisão"
        alerta={resumo.aguardandoRevisao > 0}
      />
      <KpiCard
        rotulo="Já no painel"
        valor={formatarNumero(resumo.naBase)}
        contexto={contar(
          resumo.retiradas,
          'coberta por registro oficial',
          'cobertas por registro oficial',
        )}
      />
    </GradeDeKpis>
  )
}

export function PaginaContribuicoes() {
  useTituloDaPagina('Contribuições')
  const servico = useServicoDeContribuicoes()
  const navegar = useNavigate()
  const [deslocamento, definirDeslocamento] = useState(0)
  const { fila, erro, recarregar } = useFilaDeRelatos(deslocamento)
  const [gerando, definirGerando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)

  async function gerarPacote() {
    definirGerando(true)
    definirFalha(null)
    try {
      const pacote = await servico.gerarPacote()
      void navegar(`/painel/importacoes/${pacote.id}`)
    } catch (motivo) {
      definirFalha(motivo)
      definirGerando(false)
      recarregar()
    }
  }

  return (
    <>
      <div className={estilos.topo}>
        <div>
          <h1 className={estilos.titulo}>Contribuições</h1>
          <p className={estilos.subtitulo}>
            O que chegou pelo formulário público e o que já pode entrar na base.
          </p>
        </div>
        {fila && (
          <div className={estilos.pacote}>
            <Botao
              compacto
              disabled={!podeGerarPacote(fila.resumo) || gerando}
              onClick={() => void gerarPacote()}
            >
              {gerando ? 'Gerando...' : 'Gerar pacote para importação'}
            </Botao>
            <p>{motivoDoBloqueio(fila.resumo)}</p>
          </div>
        )}
      </div>
      {erro || falha ? (
        <Aviso tipo="erro" titulo="Não foi possível concluir">
          {mensagemDeFalha(falha ?? erro)}
        </Aviso>
      ) : null}
      {!fila && !erro && <p className={estilos.subtitulo}>Carregando os relatos...</p>}
      {fila && (
        <>
          <Indicadores resumo={fila.resumo} />
          <div className={estilos.abas}>
            <Abas
              legenda="Áreas das contribuições"
              abas={[
                {
                  chave: 'pente-fino',
                  rotulo: `Pente fino (${formatarNumero(fila.resumo.aguardandoRevisao)})`,
                  conteudo: <PenteFino pares={fila.pares} aoDecidir={recarregar} />,
                },
                {
                  chave: 'ocorrencias',
                  rotulo: 'Ocorrências',
                  conteudo: (
                    <ListaDeOcorrencias
                      pagina={fila.ocorrencias}
                      deslocamento={deslocamento}
                      aoMudarDeslocamento={definirDeslocamento}
                      aoEncaminhar={recarregar}
                    />
                  ),
                },
                { chave: 'como-funciona', rotulo: 'Como funciona', conteudo: <ComoFunciona /> },
              ]}
            />
          </div>
        </>
      )}
    </>
  )
}
