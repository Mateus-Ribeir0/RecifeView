import type { ChaveDoCriterio } from '../../../../domain/prioridade'

// O critério herda a cor da fonte que o alimenta: risco vem da Defesa Civil, atraso do 156.
export const CORES_DOS_CRITERIOS: Readonly<Record<ChaveDoCriterio, string>> = {
  risco: 'var(--cor-fonte-defesa-civil)',
  vulnerabilidade: 'var(--cor-fonte-sedec)',
  atraso: 'var(--cor-fonte-156)',
  reincidencia: 'var(--cor-fonte-ouvidoria)',
}
