import { useCalendarioDaWarRoom, useQuadroDoDia } from '../../../../application/consultas/usePainel'
import { useSimulacaoDaWarRoom } from '../../../../application/consultas/useWarRoom'
import { formatarData, formatarDataLonga, formatarNumero } from '../../../../domain/formatacao'
import type { CalendarioDaWarRoom, ModoDaWarRoom } from '../../../../domain/warRoom'
import { Botao } from '../../../components/Botao'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import estilos from './PaginaWarRoom.module.css'
import { QuadroDoDia } from './QuadroDoDia'

function seloDoModo(modo: ModoDaWarRoom, passo: number, calendario: CalendarioDaWarRoom): string {
  if (modo === 'simulacao') return `Simulação, dia ${passo} de ${calendario.diasSimulados}`
  if (modo === 'fim') return `Simulação encerrada, dia ${passo} de ${calendario.diasSimulados}`
  if (modo === 'hoje') return `Hoje: bases baixadas em ${formatarData(calendario.hoje)}`
  return 'Dia sorteado'
}

export function PaginaWarRoom() {
  const consultaDoCalendario = useCalendarioDaWarRoom()
  const calendario = consultaDoCalendario.dados
  const simulacao = useSimulacaoDaWarRoom(calendario)
  const { modo, dia, passo } = simulacao
  const emSimulacao = modo === 'simulacao' || modo === 'fim'
  const consulta = useQuadroDoDia(dia, emSimulacao ? simulacao.inicio : null)

  return (
    <>
      <CabecalhoDaTela
        titulo="War Room"
        semRecorte
        fontes={['156_EMLURB', 'DEFESA_CIVIL', 'CAMARA_REQUERIMENTOS', 'OUVIDORIA']}
        ignorados={[
          'Cidade inteira, com os pesos padrão do AHP: os filtros da barra lateral não se aplicam aqui.',
        ]}
      >
        Protótipo de tela de operações: o que está parado, o que não voltou e onde agir primeiro,
        num só quadro. A tela inteira mostra o estado de um dia.
      </CabecalhoDaTela>
      <EstadoDaConsulta consulta={consultaDoCalendario}>
        {(dados) => (
          <>
            <div className={estilos.controles}>
              <Botao compacto onClick={simulacao.simularMes}>
                Simular um mês
              </Botao>
              <Botao variante="secundario" compacto onClick={simulacao.diaAleatorio}>
                Dia aleatório
              </Botao>
              <Botao
                variante="secundario"
                compacto
                disabled={modo === 'hoje'}
                onClick={simulacao.voltarParaHoje}
              >
                {modo === 'simulacao' ? 'Parar e voltar para hoje' : 'Voltar para hoje'}
              </Botao>
              <p className={estilos.legendaDosControles}>
                A simulação sorteia um dia real entre {formatarData(dados.primeiroDia)} e{' '}
                {formatarData(dados.ultimoDia)} e avança um dia a cada{' '}
                {formatarNumero(dados.segundosPorDia, 1)} s, por {dados.diasSimulados} dias. As
                bases só têm a data, sem horário. Para a sala, recolha a barra lateral e use tela
                cheia.
              </p>
            </div>
            {dia && (
              <div className={estilos.data}>
                <h2>{formatarDataLonga(dia)}</h2>
                <span className={estilos.selo}>{seloDoModo(modo, passo, dados)}</span>
              </div>
            )}
            {emSimulacao && (
              <progress
                className={estilos.progresso}
                value={passo}
                max={dados.diasSimulados}
                aria-label="Andamento da simulação"
              />
            )}
            {modo === 'hoje' && (
              <p className={estilos.legendaDosControles}>
                {formatarData(dados.hoje)} é o dia do retrato mais recente das bases, não o do
                registro mais recente. Registro mais recente de cada fonte: 156 em{' '}
                {formatarData(dados.ultimoRegistro156)}; Ouvidoria em{' '}
                {formatarData(dados.ultimoRegistroOuvidoria)}.
              </p>
            )}
          </>
        )}
      </EstadoDaConsulta>
      <EstadoDaConsulta consulta={consulta}>
        {(quadro) => <QuadroDoDia quadro={quadro} />}
      </EstadoDaConsulta>
    </>
  )
}
