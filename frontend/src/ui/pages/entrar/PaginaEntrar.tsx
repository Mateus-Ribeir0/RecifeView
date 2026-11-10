import { useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router'

import type { MotivoDaSaida } from '../../../application/autenticacao/contexto'
import { useSessao } from '../../../application/autenticacao/useSessao'
import { normalizarEmail } from '../../../domain/conta'
import { ErroDoRecifeView } from '../../../domain/erros'
import type { AreaDeAcesso } from '../../../domain/usuario'
import estilos from '../../components/Acesso.module.css'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { CampoDeTexto } from '../../components/CampoDeTexto'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { lerEstadoDeNavegacao } from '../../components/navegacao'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { validarEntrada, type ErrosDaEntrada } from './validarEntrada'

const TEXTOS: Readonly<Record<AreaDeAcesso, { titulo: string; subtitulo: string }>> = {
  cidade: {
    titulo: 'Entrar',
    subtitulo: 'Acompanhe os relatos da cidade e os números do seu bairro.',
  },
  gestao: {
    titulo: 'Entrar na área da gestão',
    subtitulo: 'Acesso restrito a gestores cadastrados pela administração.',
  },
}

const AVISOS_DE_SAIDA: Readonly<Record<MotivoDaSaida, { tipo: 'info' | 'alerta'; texto: string }>> =
  {
    saiu: { tipo: 'info', texto: 'Você saiu do RecifeView.' },
    'sessao-expirada': {
      tipo: 'alerta',
      texto: 'Sua sessão terminou. Entre de novo para continuar.',
    },
    'conta-excluida': {
      tipo: 'info',
      texto: 'Sua conta foi excluída. Nome, e-mail e bairro foram apagados.',
    },
  }

function AvisoDeSaida({ motivo }: { motivo: MotivoDaSaida | null | undefined }) {
  if (!motivo) return null
  const { tipo, texto } = AVISOS_DE_SAIDA[motivo]
  return <Aviso tipo={tipo}>{texto}</Aviso>
}

function LinksDaArea({ area }: { area: AreaDeAcesso }) {
  if (area === 'gestao') {
    return (
      <div className={estilos.links}>
        <Link to="/entrar/ajuda">Não consegue entrar?</Link>
        <Link to="/entrar">É cidadão? Entre pela área do cidadão</Link>
        <Link to="/">Voltar para a página inicial</Link>
      </div>
    )
  }
  return (
    <div className={estilos.links}>
      <p className={estilos.chamadaDeCadastro}>
        Ainda não tem conta? <Link to="/cadastrar">Criar conta</Link>
      </p>
      <Link to="/recuperar-senha">Esqueci minha senha</Link>
      <Link to="/entrar/gestao">Trabalha na gestão pública? Entre pela área da gestão</Link>
      <Link to="/">Voltar para a página inicial</Link>
    </div>
  )
}

export function PaginaEntrar({ area = 'cidade' }: { area?: AreaDeAcesso }) {
  useTituloDaPagina(TEXTOS[area].titulo)
  const { entrar } = useSessao()
  const { motivo } = lerEstadoDeNavegacao(useLocation().state)
  const [email, definirEmail] = useState('')
  const [senha, definirSenha] = useState('')
  const [erros, definirErros] = useState<ErrosDaEntrada>({})
  const [falha, definirFalha] = useState<unknown>(null)
  const [enviando, definirEnviando] = useState(false)
  const campoDeEmail = useRef<HTMLInputElement>(null)
  const campoDeSenha = useRef<HTMLInputElement>(null)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const errosEncontrados = validarEntrada(email, senha)
    definirErros(errosEncontrados)
    if (errosEncontrados.email || errosEncontrados.senha) {
      const campoComErro = errosEncontrados.email ? campoDeEmail : campoDeSenha
      campoComErro.current?.focus()
      return
    }
    definirFalha(null)
    definirEnviando(true)
    try {
      await entrar({ email: normalizarEmail(email), senha, area })
    } catch (erro) {
      definirFalha(erro)
      definirSenha('')
      campoDeSenha.current?.focus()
    } finally {
      definirEnviando(false)
    }
  }

  const precisaConfirmar =
    falha instanceof ErroDoRecifeView && falha.codigo === 'email_nao_confirmado'

  return (
    <LayoutDeAcesso tom={area}>
      <h1 className={estilos.titulo}>{TEXTOS[area].titulo}</h1>
      <p className={estilos.subtitulo}>{TEXTOS[area].subtitulo}</p>
      <div className={estilos.avisos}>
        {falha ? (
          <Aviso tipo={precisaConfirmar ? 'alerta' : 'erro'}>
            {mensagemDeFalha(falha)}{' '}
            {precisaConfirmar && (
              <Link to="/confirmar-email" state={{ email: normalizarEmail(email) }}>
                Confirmar o e-mail
              </Link>
            )}
          </Aviso>
        ) : (
          <AvisoDeSaida motivo={motivo} />
        )}
      </div>
      <form className={estilos.formulario} onSubmit={enviar} noValidate>
        <CampoDeTexto
          ref={campoDeEmail}
          rotulo="E-mail"
          type="email"
          name="email"
          autoComplete="username"
          inputMode="email"
          spellCheck={false}
          value={email}
          onChange={(evento) => definirEmail(evento.target.value)}
          erro={erros.email}
        />
        <CampoDeSenha
          ref={campoDeSenha}
          rotulo="Senha"
          name="senha"
          autoComplete="current-password"
          value={senha}
          onChange={(evento) => definirSenha(evento.target.value)}
          erro={erros.senha}
        />
        <Botao type="submit" larguraTotal disabled={enviando} aria-busy={enviando}>
          {enviando ? 'Entrando...' : 'Entrar'}
        </Botao>
      </form>
      <LinksDaArea area={area} />
    </LayoutDeAcesso>
  )
}
