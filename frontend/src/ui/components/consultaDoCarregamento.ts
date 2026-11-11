import type { Carregamento } from '../../application/carregamento/useCarregamento'
import type { ResultadoDaConsulta } from '../../application/consultas/useConsulta'

export function consultaDoCarregamento<T>(carregamento: Carregamento<T>): ResultadoDaConsulta<T> {
  return {
    dados: carregamento.dados ?? undefined,
    carregando: carregamento.carregando,
    atualizando: false,
    erro: carregamento.erro,
    tentarDeNovo: carregamento.recarregar,
  }
}
