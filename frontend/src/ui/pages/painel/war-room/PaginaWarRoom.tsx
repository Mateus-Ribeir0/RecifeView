import { useCalendarioDaWarRoom, useQuadroDoDia } from '../../../../application/consultas/usePainel'
import { useSimulacaoDaWarRoom } from '../../../../application/consultas/useWarRoom'
import { formatarData, formatarDataLonga, formatarNumero } from '../../../../domain/formatacao'
import type { CalendarioDaWarRoom, ModoDaWarRoom } from '../../../../domain/warRoom'
import { Botao } from '../../../components/Botao'
import { CabecalhoDaTela } from '../../../components/CabecalhoDaTela'
import { EstadoDaConsulta } from '../../../components/EstadoDaConsulta'
import { Icone } from '../../../components/Icone'
import estilos from './PaginaWarRoom.module.css'
import { QuadroDoDia } from './QuadroDoDia'

function seloDoModo(modo: ModoDaWarRoom, passo: number, calendario: CalendarioDaWarRoom): string {
  if (modo === 'simulacao') return `Simulação, dia ${passo} de ${calendario.diasSimulados}`
  if (modo === 'fim') return `Simulação encerrada, dia ${passo} de ${calendario.diasSimulados}`
  if (modo === 'hoje') return 'Hoje'
  return 'Dia sorteado'
}

function notasDaTela(calendario: CalendarioDaWarRoom | undefined): string[] {
  const notas = [
    'Mostra a cidade inteira, com os pesos padrão do AHP. Os filtros não se aplicam aqui.',
    'Um pedido conta como aberto da entrada até o atendimento, ou até hoje, se continua aberto nos arquivos mais recentes. Em datas antigas o estoque é um piso, porque os abertos de arquivos antigos têm destino desconhecido.',
  ]
  if (!calendario) return notas
  return [
    ...notas,
    `Hoje é ${formatarData(calendario.hoje)}, o dia do retrato mais recente das bases. Registro mais recente: 156 em ${formatarData(calendario.ultimoRegistro156)}; Ouvidoria em ${formatarData(calendario.ultimoRegistroOuvidoria)}.`,
    `A simulação sorteia um dia real entre ${formatarData(calendario.primeiroDia)} e ${formatarData(calendario.ultimoDia)} e avança um dia a cada ${formatarNumero(calendario.segundosPorDia, 1)} s, por ${calendario.diasSimulados} dias. As bases só têm a data, sem horário.`,
  ]
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
        fontes={['156_EMLURB', 'DEFESA_CIVIL', 'CAMARA_REQUERIMENTOS', 'OUVIDORIA']}
        notas={notasDaTela(calendario)}
        acoes={
          <>
            <Botao compacto onClick={simulacao.simularMes}>
              <Icone nome="reproduzir" tamanho={16} />
              Simular um mês
            </Botao>
            <Botao variante="secundario" compacto onClick={simulacao.diaAleatorio}>
              <Icone nome="sortear" tamanho={16} />
              Dia aleatório
            </Botao>
            <Botao
              variante="secundario"
              compacto
              disabled={modo === 'hoje'}
              onClick={simulacao.voltarParaHoje}
            >
              <Icone nome="voltar" tamanho={16} />
              {modo === 'simulacao' ? 'Parar' : 'Hoje'}
            </Botao>
          </>
        }
      >
        O que está parado, o que não voltou e onde agir primeiro, num só quadro.
      </CabecalhoDaTela>
      <EstadoDaConsulta consulta={consultaDoCalendario}>
        {(dados) => (
          <>
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
          </>
        )}
      </EstadoDaConsulta>
      <EstadoDaConsulta consulta={consulta}>
        {(quadro) => <QuadroDoDia quadro={quadro} />}
      </EstadoDaConsulta>
    </>
  )
}
