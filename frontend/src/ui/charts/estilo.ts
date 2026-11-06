import type { CodigoDaFonte } from '../../domain/fontes'

export const COR = {
  principal: 'var(--cor-azul-principal)',
  marinho: 'var(--cor-azul-marinho)',
  medio: 'var(--cor-mapa-3)',
  claro: 'var(--cor-mapa-2)',
  fundo: 'var(--cor-branco)',
  contexto: 'var(--cor-contexto)',
  grade: 'var(--cor-borda)',
  texto: 'var(--cor-preto)',
  eixo: 'var(--cor-texto-terciario)',
  alerta: 'var(--cor-alerta-texto)',
} as const

export const CORES_DAS_FONTES: Readonly<Record<CodigoDaFonte, string>> = {
  '156_EMLURB': 'var(--cor-fonte-156)',
  OUVIDORIA: 'var(--cor-fonte-ouvidoria)',
  CAMARA_REQUERIMENTOS: 'var(--cor-fonte-camara)',
  DEFESA_CIVIL: 'var(--cor-fonte-defesa-civil)',
  SEDEC_CHAMADOS: 'var(--cor-fonte-sedec)',
  FORMULARIO_PUBLICO: 'var(--cor-fonte-formulario)',
}

export const ESCALA_DO_MAPA: readonly string[] = [
  'var(--cor-mapa-1)',
  'var(--cor-mapa-2)',
  'var(--cor-mapa-3)',
  'var(--cor-mapa-4)',
  'var(--cor-mapa-5)',
]

export const EIXO = {
  tick: { fontSize: 12, fontWeight: 500, fill: COR.eixo },
  tickLine: false,
  axisLine: { stroke: COR.grade },
} as const

export const ANIMACAO = { isAnimationActive: false } as const
export const LARGURA_MAXIMA_DA_BARRA = 24
export const RAIO_DA_BARRA_VERTICAL: [number, number, number, number] = [4, 4, 0, 0]
export const RAIO_DA_BARRA_HORIZONTAL: [number, number, number, number] = [0, 4, 4, 0]
