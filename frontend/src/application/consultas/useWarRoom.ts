import { useCallback, useEffect, useState } from 'react'

import {
  diasEntre,
  somarDias,
  type CalendarioDaWarRoom,
  type ModoDaWarRoom,
} from '../../domain/warRoom'

const MILISSEGUNDOS_POR_SEGUNDO = 1000

interface EstadoDaSimulacao {
  modo: ModoDaWarRoom
  dia: string | null
  inicio: string | null
}

export interface SimulacaoDaWarRoom {
  modo: ModoDaWarRoom
  dia: string | null
  inicio: string | null
  passo: number
  simularMes: () => void
  diaAleatorio: () => void
  voltarParaHoje: () => void
}

function sortearDia(primeiro: string, ultimo: string): string {
  return somarDias(primeiro, Math.floor(Math.random() * (diasEntre(primeiro, ultimo) + 1)))
}

export function useSimulacaoDaWarRoom(
  calendario: CalendarioDaWarRoom | undefined,
): SimulacaoDaWarRoom {
  const [estado, definirEstado] = useState<EstadoDaSimulacao>({
    modo: 'hoje',
    dia: null,
    inicio: null,
  })
  const dia = estado.dia ?? calendario?.hoje ?? null
  const simulando = estado.modo === 'simulacao'

  useEffect(() => {
    if (!simulando || !calendario) return
    const intervalo = setInterval(() => {
      definirEstado((atual) => {
        if (!atual.dia || !atual.inicio) return atual
        const fim = somarDias(atual.inicio, calendario.diasSimulados - 1)
        if (atual.dia >= fim) return { ...atual, modo: 'fim' }
        return { ...atual, dia: somarDias(atual.dia, 1) }
      })
    }, calendario.segundosPorDia * MILISSEGUNDOS_POR_SEGUNDO)
    return () => clearInterval(intervalo)
  }, [simulando, calendario])

  const simularMes = useCallback(() => {
    if (!calendario) return
    const ultimoInicio = somarDias(calendario.ultimoDia, -calendario.diasSimulados)
    const inicio = sortearDia(calendario.primeiroDia, ultimoInicio)
    definirEstado({ modo: 'simulacao', dia: inicio, inicio })
  }, [calendario])

  const diaAleatorio = useCallback(() => {
    if (!calendario) return
    const sorteado = sortearDia(calendario.primeiroDia, calendario.ultimoDia)
    definirEstado({ modo: 'dia', dia: sorteado, inicio: null })
  }, [calendario])

  const voltarParaHoje = useCallback(() => {
    definirEstado({ modo: 'hoje', dia: null, inicio: null })
  }, [])

  const passo = estado.inicio && dia ? diasEntre(estado.inicio, dia) + 1 : 0
  return {
    modo: estado.modo,
    dia,
    inicio: estado.inicio,
    passo,
    simularMes,
    diaAleatorio,
    voltarParaHoje,
  }
}
