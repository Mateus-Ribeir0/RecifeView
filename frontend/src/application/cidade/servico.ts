import type { FiltroDaCidade, IndicadoresDoBairro, OcorrenciaDaCidade } from '../../domain/cidade'

export interface ServicoDaCidade {
  ocorrencias(filtro: FiltroDaCidade): Promise<readonly OcorrenciaDaCidade[]>
  meuBairro(bairro: string): Promise<IndicadoresDoBairro>
}
