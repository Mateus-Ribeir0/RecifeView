import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { ContextoDaSessao, type EstadoDaSessao } from './contexto'
import type {
  ConfirmacaoDeEmail,
  Credenciais,
  DadosDaConta,
  NovaConta,
  NovaSenhaComCodigo,
  ServicoDeAutenticacao,
  TrocaDeSenha,
} from './servico'

interface Propriedades {
  servico: ServicoDeAutenticacao
  children: ReactNode
}

export function ProvedorDeSessao({ servico, children }: Propriedades) {
  const [estado, definirEstado] = useState<EstadoDaSessao>({ situacao: 'verificando' })

  useEffect(() => {
    let montado = true
    servico.restaurarSessao().then(
      (usuario) => {
        if (!montado) return
        definirEstado(
          usuario ? { situacao: 'autenticada', usuario } : { situacao: 'anonima', motivo: null },
        )
      },
      () => {
        if (montado) definirEstado({ situacao: 'anonima', motivo: null })
      },
    )
    const pararDeObservar = servico.observarPerdaDeSessao(() =>
      definirEstado({ situacao: 'anonima', motivo: 'sessao-expirada' }),
    )
    return () => {
      montado = false
      pararDeObservar()
    }
  }, [servico])

  const entrar = useCallback(
    async (credenciais: Credenciais) => {
      const usuario = await servico.entrar(credenciais)
      definirEstado({ situacao: 'autenticada', usuario })
      return usuario
    },
    [servico],
  )

  const sair = useCallback(async () => {
    try {
      await servico.sair()
    } finally {
      definirEstado({ situacao: 'anonima', motivo: 'saiu' })
    }
  }, [servico])

  const trocarSenha = useCallback(
    async (troca: TrocaDeSenha) => {
      const usuario = await servico.trocarSenha(troca)
      definirEstado({ situacao: 'autenticada', usuario })
      return usuario
    },
    [servico],
  )

  const confirmarEmail = useCallback(
    async (confirmacao: ConfirmacaoDeEmail) => {
      const usuario = await servico.confirmarEmail(confirmacao)
      definirEstado({ situacao: 'autenticada', usuario })
      return usuario
    },
    [servico],
  )

  const atualizarConta = useCallback(
    async (dados: DadosDaConta) => {
      const usuario = await servico.atualizarConta(dados)
      definirEstado({ situacao: 'autenticada', usuario })
      return usuario
    },
    [servico],
  )

  const excluirConta = useCallback(
    async (senha: string) => {
      await servico.excluirConta(senha)
      definirEstado({ situacao: 'anonima', motivo: 'conta-excluida' })
    },
    [servico],
  )

  const sessao = useMemo(
    () => ({
      estado,
      entrar,
      sair,
      trocarSenha,
      confirmarEmail,
      atualizarConta,
      excluirConta,
      criarConta: (conta: NovaConta) => servico.criarConta(conta),
      reenviarCodigo: (email: string) => servico.reenviarCodigo(email),
      pedirNovaSenha: (email: string) => servico.pedirNovaSenha(email),
      criarNovaSenha: (pedido: NovaSenhaComCodigo) => servico.criarNovaSenha(pedido),
    }),
    [servico, estado, entrar, sair, trocarSenha, confirmarEmail, atualizarConta, excluirConta],
  )

  return <ContextoDaSessao value={sessao}>{children}</ContextoDaSessao>
}
