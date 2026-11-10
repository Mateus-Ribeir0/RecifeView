import type {
  FiltroDaCidade,
  IndicadoresDoBairro,
  MeuRelato,
  OcorrenciaDaCidade,
} from '../../domain/cidade'

export interface ServicoDaCidade {
  ocorrencias(filtro: FiltroDaCidade): Promise<readonly OcorrenciaDaCidade[]>
  meuBairro(bairro: string): Promise<IndicadoresDoBairro>
  meusRelatos(): Promise<readonly MeuRelato[]>
}
