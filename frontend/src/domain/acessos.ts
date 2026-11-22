import type { Orgao } from './encaminhamentos'

export type SituacaoDoAcesso = 'convite_enviado' | 'convite_vencido' | 'ativo' | 'desativado'

export interface AcessoCorporativo {
  id: string
  nome: string
  email: string
  orgao: Orgao
  nomeDoOrgao: string
  situacao: SituacaoDoAcesso
  criadoEm: string
  conviteExpiraEm: string | null
  ultimoAcessoEm: string | null
}

export interface ListaDeAcessos {
  podeAlterar: boolean
  itens: readonly AcessoCorporativo[]
}

export interface DadosDoAcesso {
  nome: string
  orgao: Orgao
}

export interface NovoAcesso extends DadosDoAcesso {
  email: string
}

export interface ConviteDeAcesso {
  nome: string
  email: string
  orgao: Orgao
  nomeDoOrgao: string
  expiraEm: string
}

export const ROTULOS_DAS_SITUACOES_DO_ACESSO: Readonly<Record<SituacaoDoAcesso, string>> = {
  convite_enviado: 'Convite enviado',
  convite_vencido: 'Convite vencido',
  ativo: 'Ativo',
  desativado: 'Desativado',
}

export function podeReenviarConvite(situacao: SituacaoDoAcesso): boolean {
  return situacao === 'convite_enviado' || situacao === 'convite_vencido'
}

export function contarPorSituacao(
  acessos: readonly AcessoCorporativo[],
): Readonly<Record<SituacaoDoAcesso, number>> {
  const contagem: Record<SituacaoDoAcesso, number> = {
    convite_enviado: 0,
    convite_vencido: 0,
    ativo: 0,
    desativado: 0,
  }
  acessos.forEach((acesso) => {
    contagem[acesso.situacao] += 1
  })
  return contagem
}

export function orgaosComAcessoAtivo(acessos: readonly AcessoCorporativo[]): number {
  return new Set(acessos.filter((item) => item.situacao === 'ativo').map((item) => item.orgao)).size
}
