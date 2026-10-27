import { describe, expect, it, vi } from 'vitest'

import { ErroDoRecifeView } from '../../domain/erros'
import { ClienteHttp } from './cliente'

function resposta(status: number, corpo?: unknown): Response {
  return new Response(corpo === undefined ? null : JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const ERRO_DE_SESSAO = { erro: { codigo: 'sessao_invalida', mensagem: 'Sua sessão terminou.' } }

describe('ClienteHttp', () => {
  it('envia o token de acesso nas requisições autenticadas', async () => {
    const buscar = vi.fn().mockResolvedValue(resposta(200, { ok: true }))
    const cliente = new ClienteHttp('/api/v1', buscar)
    cliente.definirTokenDeAcesso('token-1')

    await cliente.enviar('/autenticacao/eu', { autenticada: true })

    const [, opcoes] = buscar.mock.calls[0] as [string, RequestInit]
    expect(new Headers(opcoes.headers).get('Authorization')).toBe('Bearer token-1')
    expect(opcoes.credentials).toBe('include')
  })

  it('renova o acesso uma vez e repete a requisição depois de um 401', async () => {
    const buscar = vi
      .fn()
      .mockResolvedValueOnce(resposta(401, ERRO_DE_SESSAO))
      .mockResolvedValueOnce(resposta(200, { nome: 'Gestora' }))
    const cliente = new ClienteHttp('/api/v1', buscar)
    const renovador = vi.fn().mockResolvedValue(true)
    cliente.definirRenovador(renovador)

    const corpo = await cliente.enviar<{ nome: string }>('/autenticacao/eu', { autenticada: true })

    expect(corpo.nome).toBe('Gestora')
    expect(renovador).toHaveBeenCalledTimes(1)
    expect(buscar).toHaveBeenCalledTimes(2)
  })

  it('avisa a perda de sessão quando a renovação falha', async () => {
    const buscar = vi.fn().mockResolvedValue(resposta(401, ERRO_DE_SESSAO))
    const cliente = new ClienteHttp('/api/v1', buscar)
    cliente.definirRenovador(vi.fn().mockResolvedValue(false))
    const aoPerder = vi.fn()
    cliente.observarPerdaDeSessao(aoPerder)

    await expect(cliente.enviar('/autenticacao/eu', { autenticada: true })).rejects.toMatchObject({
      codigo: 'sessao_invalida',
    })
    expect(aoPerder).toHaveBeenCalledTimes(1)
  })

  it('converte o bloqueio da conta com o horário de desbloqueio', async () => {
    const corpo = {
      erro: {
        codigo: 'conta_bloqueada',
        mensagem: 'Muitas tentativas.',
        detalhes: { desbloqueio_em: '2026-10-26T15:30:00+00:00' },
      },
    }
    const cliente = new ClienteHttp('/api/v1', vi.fn().mockResolvedValue(resposta(429, corpo)))

    const envio = cliente.enviar('/autenticacao/entrar', { metodo: 'POST' })

    await expect(envio).rejects.toBeInstanceOf(ErroDoRecifeView)
    await expect(envio).rejects.toMatchObject({
      codigo: 'conta_bloqueada',
      desbloqueioEm: new Date('2026-10-26T15:30:00Z'),
    })
  })

  it('trata falha de rede e erro do servidor como serviço indisponível', async () => {
    const semRede = new ClienteHttp('/api/v1', vi.fn().mockRejectedValue(new TypeError('falhou')))
    await expect(semRede.enviar('/saude')).rejects.toMatchObject({ codigo: 'servico_indisponivel' })

    const comErro = new ClienteHttp('/api/v1', vi.fn().mockResolvedValue(resposta(502)))
    await expect(comErro.enviar('/saude')).rejects.toMatchObject({ codigo: 'servico_indisponivel' })
  })

  it('devolve vazio numa resposta 204', async () => {
    const cliente = new ClienteHttp('/api/v1', vi.fn().mockResolvedValue(resposta(204)))
    await expect(cliente.enviar('/autenticacao/sair', { metodo: 'POST' })).resolves.toBeUndefined()
  })
})
