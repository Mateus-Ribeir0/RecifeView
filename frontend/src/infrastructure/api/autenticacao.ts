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
  bairro_oficial: string | null
  recebe_avisos?: boolean
}

interface PedidoRecebidoJson {
  mensagem: string
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
  contas: '/contas',
  recuperar: '/contas/recuperar-senha',
  novaSenha: '/contas/nova-senha',
  minhaConta: '/contas/eu',
  avisosDaConta: '/contas/eu/avisos',
  excluir: '/contas/eu/excluir',
} as const

function paraUsuario(json: UsuarioJson): Usuario {
  return {
    id: json.id,
    nome: json.nome,
    email: json.email,
    perfil: json.perfil,
    deveTrocarSenha: json.deve_trocar_senha,
    bairroOficial: json.bairro_oficial ?? null,
    recebeAvisos: json.recebe_avisos ?? true,
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
    async entrar({ email, senha, area = 'cidade' }) {
      const corpo = { email, senha, area }
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
    async criarConta(conta) {
      const corpo = {
        nome: conta.nome,
        email: conta.email,
        senha: conta.senha,
        bairro_oficial: conta.bairroOficial,
        aceitou_os_termos: conta.aceitouOsTermos,
        site: conta.site,
      }
      return guardarAcesso(
        await cliente.enviar<AcessoJson>(CAMINHOS.contas, { metodo: 'POST', corpo }),
      )
    },
    async pedirNovaSenha(email) {
      const resposta = await cliente.enviar<PedidoRecebidoJson>(CAMINHOS.recuperar, {
        metodo: 'POST',
        corpo: { email },
      })
      return resposta.mensagem
    },
    async criarNovaSenha({ email, codigo, novaSenha }) {
      await cliente.enviar<unknown>(CAMINHOS.novaSenha, {
        metodo: 'POST',
        corpo: { email, codigo, nova_senha: novaSenha },
      })
    },
    async atualizarConta({ nome, bairroOficial }) {
      const usuario = await cliente.enviar<UsuarioJson>(CAMINHOS.minhaConta, {
        metodo: 'PUT',
        corpo: { nome, bairro_oficial: bairroOficial },
        autenticada: true,
      })
      return paraUsuario(usuario)
    },
    async definirAvisos(recebeAvisos) {
      const usuario = await cliente.enviar<UsuarioJson>(CAMINHOS.avisosDaConta, {
        metodo: 'PUT',
        corpo: { recebe_avisos: recebeAvisos },
        autenticada: true,
      })
      return paraUsuario(usuario)
    },
    async excluirConta(senha) {
      try {
        await cliente.enviar<unknown>(CAMINHOS.excluir, {
          metodo: 'POST',
          corpo: { senha },
          autenticada: true,
        })
      } finally {
        cliente.definirTokenDeAcesso(null)
      }
    },
  }
}
