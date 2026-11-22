import { describe, expect, it } from 'vitest'

import { OCORRENCIA_DO_ORGAO } from '../testes/corporativoFalso'
import {
  contarPorSituacao,
  orgaosComAcessoAtivo,
  podeReenviarConvite,
  type AcessoCorporativo,
  type SituacaoDoAcesso,
} from './acessos'
import { descreverPrazo, mesmoProblemaQueDaParaJuntar, prazoPedeAtencao } from './corporativo'
import type { Orgao } from './encaminhamentos'
import { chegouNovidade, descreverQuando } from './notificacoes'
import { eCorporativo, eDaGestao, inicioDoPerfil, podeAbrir } from './usuario'

describe('área corporativa', () => {
  it('escreve o prazo como o órgão lê', () => {
    expect(descreverPrazo(0)).toBe('vence hoje')
    expect(descreverPrazo(1)).toBe('vence em 1 dia')
    expect(descreverPrazo(12)).toBe('vence em 12 dias')
    expect(descreverPrazo(-3)).toBe('venceu há 3 dias')
  })

  it('pede atenção na última semana do prazo e depois dele', () => {
    expect(prazoPedeAtencao({ atrasado: false, diasParaOPrazo: 8 })).toBe(false)
    expect(prazoPedeAtencao({ atrasado: false, diasParaOPrazo: 7 })).toBe(true)
    expect(prazoPedeAtencao({ atrasado: true, diasParaOPrazo: -1 })).toBe(true)
  })

  it('só junta o mesmo problema do próprio órgão e ainda aberto', () => {
    const juntaveis = mesmoProblemaQueDaParaJuntar(OCORRENCIA_DO_ORGAO.mesmoProblema)

    expect(juntaveis.map((item) => item.codigo)).toEqual(['ENC-2026-000008'])
  })
})

describe('perfil corporativo', () => {
  it('abre só a área corporativa', () => {
    expect(inicioDoPerfil('CORPORATIVO')).toBe('/corporativo')
    expect(podeAbrir('CORPORATIVO', '/corporativo/ocorrencias/7')).toBe(true)
    expect(podeAbrir('CORPORATIVO', '/painel/encaminhamentos')).toBe(false)
    expect(podeAbrir('CORPORATIVO', '/cidade/meus-pedidos')).toBe(false)
    expect(podeAbrir('GESTOR', '/corporativo')).toBe(false)
  })

  it('não é da gestão', () => {
    expect(eDaGestao('CORPORATIVO')).toBe(false)
    expect(eCorporativo('CORPORATIVO')).toBe(true)
    expect(eDaGestao('ADMINISTRADOR')).toBe(true)
  })
})

describe('acessos corporativos', () => {
  function acesso(orgao: Orgao, situacao: SituacaoDoAcesso): AcessoCorporativo {
    return {
      id: `${orgao}-${situacao}-${Math.random()}`,
      nome: 'Pessoa',
      email: 'pessoa@orgao.exemplo',
      orgao,
      nomeDoOrgao: orgao,
      situacao,
      criadoEm: '2026-11-01T12:00:00Z',
      conviteExpiraEm: null,
      ultimoAcessoEm: null,
    }
  }
  const acessos = [
    acesso('EMLURB', 'ativo'),
    acesso('COMPESA', 'ativo'),
    acesso('COMPESA', 'ativo'),
    acesso('COMPESA', 'convite_vencido'),
  ]

  it('conta por situação e por órgão com acesso ativo', () => {
    expect(contarPorSituacao(acessos).ativo).toBe(3)
    expect(orgaosComAcessoAtivo(acessos)).toBe(2)
  })

  it('reenvia convite só enquanto ninguém definiu a senha', () => {
    expect(podeReenviarConvite('convite_vencido')).toBe(true)
    expect(podeReenviarConvite('ativo')).toBe(false)
  })
})

describe('notificações', () => {
  const agora = new Date('2026-11-19T12:00:00Z')

  it('diz há quanto tempo chegou', () => {
    expect(descreverQuando('2026-11-19T11:59:40Z', agora)).toBe('agora')
    expect(descreverQuando('2026-11-19T11:15:00Z', agora)).toBe('há 45 min')
    expect(descreverQuando('2026-11-19T07:00:00Z', agora)).toBe('há 5 h')
    expect(descreverQuando('2026-11-18T09:00:00Z', agora)).toBe('ontem')
  })

  it('percebe quando chega uma notificação nova', () => {
    const vazia = { naoLidas: 0, itens: [] }
    const comUma = {
      naoLidas: 1,
      itens: [
        {
          id: 3,
          titulo: 't',
          texto: 'x',
          caminho: '/',
          criadaEm: '2026-11-19T11:00:00Z',
          lida: false,
        },
      ],
    }

    expect(chegouNovidade(vazia, comUma)).toBe(true)
    expect(chegouNovidade(comUma, comUma)).toBe(false)
  })
})
