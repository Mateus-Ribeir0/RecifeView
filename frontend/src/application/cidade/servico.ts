import type { FiltroDaCidade, MeuRelato, OcorrenciaDaCidade } from '../../domain/cidade'

export interface ServicoDaCidade {
  ocorrencias(filtro: FiltroDaCidade): Promise<readonly OcorrenciaDaCidade[]>
  meusRelatos(): Promise<readonly MeuRelato[]>
}
