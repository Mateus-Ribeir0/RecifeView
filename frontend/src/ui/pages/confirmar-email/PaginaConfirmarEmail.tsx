import { useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import {
  codigoCompleto,
  digitosDoCodigo,
  emailValido,
  normalizarEmail,
} from '../../../domain/conta'
import estilos from '../../components/Acesso.module.css'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CampoDeCodigo } from '../../components/CampoDeCodigo'
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { CampoDeTexto } from '../../components/CampoDeTexto'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useEsperaParaReenviar } from '../../components/useEsperaParaReenviar'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'

function emailDoEstado(estado: unknown): string {
  if (typeof estado !== 'object' || estado === null || !('email' in estado)) return ''
  return typeof estado.email === 'string' ? estado.email : ''
}

export function PaginaConfirmarEmail() {
  useTituloDaPagina('Confirmar o e-mail')
  const { confirmarEmail, reenviarCodigo } = useSessao()
  const estado: unknown = useLocation().state
  const [email, definirEmail] = useState(() => emailDoEstado(estado))
  const [codigo, definirCodigo] = useState('')
  const [senha, definirSenha] = useState('')
  const [falha, definirFalha] = useState<unknown>(null)
  const [aviso, definirAviso] = useState<string | null>(null)
  const [enviando, definirEnviando] = useState(false)
  const [restante, reiniciarEspera] = useEsperaParaReenviar()

  async function confirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!emailValido(email) || !codigoCompleto(codigo) || !senha) {
      definirFalha(new Error('Preencha o e-mail, os 6 dígitos do código e a sua senha.'))
      return
    }
    definirEnviando(true)
    definirFalha(null)
    try {
      await confirmarEmail({
        email: normalizarEmail(email),
        codigo: digitosDoCodigo(codigo),
        senha,
      })
    } catch (erro) {
      definirFalha(erro)
      definirSenha('')
      definirEnviando(false)
    }
  }

  async function reenviar() {
    if (!emailValido(email)) {
      definirFalha(new Error('Informe o e-mail usado no cadastro.'))
      return
    }
    definirFalha(null)
    try {
      definirAviso(await reenviarCodigo(normalizarEmail(email)))
      reiniciarEspera()
    } catch (erro) {
      definirFalha(erro)
    }
  }

  return (
    <LayoutDeAcesso tom="cidade">
      <h1 className={estilos.titulo}>Confirmar o e-mail</h1>
      <p className={estilos.subtitulo}>
        Use o código que enviamos e a senha que você escolheu no cadastro.
      </p>
      <div className={estilos.avisos}>
        {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
        {aviso && !falha ? <Aviso tipo="info">{aviso}</Aviso> : null}
      </div>
      <form className={estilos.formulario} onSubmit={confirmar} noValidate>
        <CampoDeTexto
          rotulo="E-mail"
          type="email"
          autoComplete="username"
          inputMode="email"
          spellCheck={false}
          value={email}
          onChange={(evento) => definirEmail(evento.target.value)}
        />
        <CampoDeCodigo valor={codigo} aoMudar={definirCodigo} />
        <CampoDeSenha
          rotulo="Senha"
          autoComplete="current-password"
          value={senha}
          onChange={(evento) => definirSenha(evento.target.value)}
        />
        <Botao type="submit" larguraTotal disabled={enviando} aria-busy={enviando}>
          {enviando ? 'Confirmando...' : 'Confirmar e entrar'}
        </Botao>
      </form>
      <div className={estilos.links}>
        <button
          type="button"
          className={estilos.botaoDeLink}
          disabled={restante > 0}
          onClick={() => void reenviar()}
        >
          {restante > 0 ? `Reenviar o código em ${restante} s` : 'Reenviar o código'}
        </button>
        <Link to="/cadastrar">Fazer o cadastro de novo</Link>
        <Link to="/entrar">Voltar para a entrada</Link>
      </div>
    </LayoutDeAcesso>
  )
}
