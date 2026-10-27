import { useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router'

import type { MotivoDaSaida } from '../../../application/autenticacao/contexto'
import { useSessao } from '../../../application/autenticacao/useSessao'
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

function AvisoDeSaida({ motivo }: { motivo: MotivoDaSaida | null | undefined }) {
  if (motivo === 'saiu') return <Aviso tipo="info">Você saiu do RecifeView.</Aviso>
  if (motivo === 'sessao-expirada') {
    return <Aviso tipo="alerta">Sua sessão terminou. Entre de novo para continuar.</Aviso>
  }
  return null
}

export function PaginaEntrar() {
  useTituloDaPagina('Entrar')
  const { entrar } = useSessao()
  const { motivo } = lerEstadoDeNavegacao(useLocation().state)
  const [email, definirEmail] = useState('')
  const [senha, definirSenha] = useState('')
  const [erros, definirErros] = useState<ErrosDaEntrada>({})
  const [falha, definirFalha] = useState<string | null>(null)
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
      await entrar({ email: email.trim(), senha })
    } catch (erro) {
      definirFalha(mensagemDeFalha(erro))
      definirSenha('')
      campoDeSenha.current?.focus()
    } finally {
      definirEnviando(false)
    }
  }

  return (
    <LayoutDeAcesso>
      <h1 className={estilos.titulo}>Entrar</h1>
      <p className={estilos.subtitulo}>Acesso restrito a gestores públicos cadastrados.</p>
      <div className={estilos.avisos}>
        {falha ? <Aviso tipo="erro">{falha}</Aviso> : <AvisoDeSaida motivo={motivo} />}
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
      <div className={estilos.links}>
        <Link to="/entrar/ajuda">Não consegue entrar?</Link>
        <Link to="/">Voltar para a página inicial</Link>
      </div>
    </LayoutDeAcesso>
  )
}
