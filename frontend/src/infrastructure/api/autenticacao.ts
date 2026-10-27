import type { ServicoDeAutenticacao } from '../../application/autenticacao/servico'
import { ErroDoRecifeView } from '../../domain/erros'
import type { Perfil, Usuario } from '../../domain/usuario'
import type { ClienteHttp } from './cliente'

interface UsuarioJson {
  id: string
  nome: string
  email: string
  perfil: Perfil
  deve_trocar_senha: boolean
}

interface AcessoJson {
  token_de_acesso: string
  expira_em: string
  usuario: UsuarioJson
}

const CAMINHOS = {
  entrar: '/autenticacao/entrar',
  renovar: '/autenticacao/renovar',
  sair: '/autenticacao/sair',
  trocarSenha: '/autenticacao/trocar-senha',
} as const

function paraUsuario(json: UsuarioJson): Usuario {
  return {
    id: json.id,
    nome: json.nome,
    email: json.email,
    perfil: json.perfil,
    deveTrocarSenha: json.deve_trocar_senha,
  }
}

export function criarServicoDeAutenticacao(cliente: ClienteHttp): ServicoDeAutenticacao {
  function guardarAcesso(acesso: AcessoJson): Usuario {
    cliente.definirTokenDeAcesso(acesso.token_de_acesso)
    return paraUsuario(acesso.usuario)
  }

  async function renovar(): Promise<Usuario | null> {
    try {
      return guardarAcesso(await cliente.enviar<AcessoJson>(CAMINHOS.renovar, { metodo: 'POST' }))
    } catch (erro) {
      if (erro instanceof ErroDoRecifeView && erro.codigo === 'sessao_invalida') {
        cliente.definirTokenDeAcesso(null)
        return null
      }
      throw erro
    }
  }

  cliente.definirRenovador(async () => (await renovar()) !== null)

  return {
    async entrar({ email, senha }) {
      const corpo = { email, senha }
      return guardarAcesso(
        await cliente.enviar<AcessoJson>(CAMINHOS.entrar, { metodo: 'POST', corpo }),
      )
    },
    restaurarSessao: renovar,
    async sair() {
      try {
        await cliente.enviar<unknown>(CAMINHOS.sair, { metodo: 'POST' })
      } finally {
        cliente.definirTokenDeAcesso(null)
      }
    },
    async trocarSenha({ senhaAtual, novaSenha }) {
      const corpo = { senha_atual: senhaAtual, nova_senha: novaSenha }
      return guardarAcesso(
        await cliente.enviar<AcessoJson>(CAMINHOS.trocarSenha, {
          metodo: 'POST',
          corpo,
          autenticada: true,
        }),
      )
    },
    observarPerdaDeSessao: (aoPerder) => cliente.observarPerdaDeSessao(aoPerder),
  }
}
