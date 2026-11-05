import type { ReactNode } from 'react'

import type { ResultadoDaConsulta } from '../../application/consultas/useConsulta'
import { Aviso } from './Aviso'
import { Botao } from './Botao'
import estilos from './EstadoDaConsulta.module.css'
import { mensagemDeFalha } from './mensagemDeFalha'

interface Propriedades<T> {
  consulta: ResultadoDaConsulta<T>
  estaVazia?: (dados: T) => boolean
  mensagemDeVazio?: string
  children: (dados: T) => ReactNode
}

const MENSAGEM_DE_VAZIO = 'Nenhuma demanda para estes filtros.'

export function EstadoDaConsulta<T>({
  consulta,
  estaVazia,
  mensagemDeVazio = MENSAGEM_DE_VAZIO,
  children,
}: Propriedades<T>) {
  if (consulta.erro) {
    return (
      <Aviso tipo="erro" titulo="Não foi possível carregar estes dados">
        <p>{mensagemDeFalha(consulta.erro)}</p>
        <Botao variante="secundario" compacto onClick={consulta.tentarDeNovo}>
          Tentar de novo
        </Botao>
      </Aviso>
    )
  }
  if (consulta.dados === undefined) {
    return <div className={estilos.esqueleto} role="status" aria-label="Carregando dados" />
  }
  if (estaVazia?.(consulta.dados)) return <p className={estilos.vazio}>{mensagemDeVazio}</p>
  return <>{children(consulta.dados)}</>
}
