export type CodigoDaFonte =
  | '156_EMLURB'
  | 'DEFESA_CIVIL'
  | 'OUVIDORIA'
  | 'SEDEC_CHAMADOS'
  | 'CAMARA_REQUERIMENTOS'
  | 'FORMULARIO_PUBLICO'

export const ORDEM_DAS_FONTES: readonly CodigoDaFonte[] = [
  '156_EMLURB',
  'DEFESA_CIVIL',
  'OUVIDORIA',
  'SEDEC_CHAMADOS',
  'CAMARA_REQUERIMENTOS',
  'FORMULARIO_PUBLICO',
]

export const FONTES_DE_ARQUIVO: readonly CodigoDaFonte[] = ORDEM_DAS_FONTES.filter(
  (fonte) => fonte !== 'FORMULARIO_PUBLICO',
)

export const NOMES_DAS_FONTES: Readonly<Record<CodigoDaFonte, string>> = {
  '156_EMLURB': 'Central 156 / Emlurb',
  DEFESA_CIVIL: 'Defesa Civil',
  OUVIDORIA: 'Ouvidoria',
  SEDEC_CHAMADOS: 'SEDEC, áreas de risco',
  CAMARA_REQUERIMENTOS: 'Câmara Municipal',
  FORMULARIO_PUBLICO: 'Formulário público',
}

export const NOMES_CURTOS_DAS_FONTES: Readonly<Record<CodigoDaFonte, string>> = {
  '156_EMLURB': '156',
  DEFESA_CIVIL: 'Defesa Civil',
  OUVIDORIA: 'Ouvidoria',
  SEDEC_CHAMADOS: 'SEDEC',
  CAMARA_REQUERIMENTOS: 'Câmara',
  FORMULARIO_PUBLICO: 'Formulário',
}

export function nomeDaFonte(codigo: string | null | undefined): string {
  if (!codigo) return 'várias fontes'
  return NOMES_DAS_FONTES[codigo as CodigoDaFonte] ?? codigo
}
