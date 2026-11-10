import { useId, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import {
  avaliarSenhaDoCadastro,
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
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { ListaDeRequisitos } from '../definir-senha/ListaDeRequisitos'

type Etapa = 'email' | 'codigo' | 'pronto'

export function PaginaRecuperarSenha() {
  useTituloDaPagina('Esqueci minha senha')
  const { pedirNovaSenha, criarNovaSenha } = useSessao()
  const idDosRequisitos = useId()
  const [etapa, definirEtapa] = useState<Etapa>('email')
  const [email, definirEmail] = useState('')
  const [codigo, definirCodigo] = useState('')
  const [senha, definirSenha] = useState('')
  const [confirmacao, definirConfirmacao] = useState('')
  const [aviso, definirAviso] = useState<string | null>(null)
  const [falha, definirFalha] = useState<unknown>(null)
  const [enviando, definirEnviando] = useState(false)
  const requisitos = avaliarSenhaDoCadastro({ senha, confirmacao, email })

  async function executar(acao: () => Promise<void>) {
    definirEnviando(true)
    definirFalha(null)
    try {
      await acao()
    } catch (erro) {
      definirFalha(erro)
    } finally {
      definirEnviando(false)
    }
  }

  function pedirCodigo(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!emailValido(email)) {
      definirFalha(new Error('Informe o e-mail da sua conta.'))
      return
    }
    void executar(async () => {
      definirAviso(await pedirNovaSenha(normalizarEmail(email)))
      definirEtapa('codigo')
    })
  }

  function trocarSenha(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!codigoCompleto(codigo) || !requisitos.every((requisito) => requisito.atendido)) {
      definirFalha(new Error('Confira o código e as regras da nova senha.'))
      return
    }
    void executar(async () => {
      await criarNovaSenha({
        email: normalizarEmail(email),
        codigo: digitosDoCodigo(codigo),
        novaSenha: senha,
      })
      definirEtapa('pronto')
    })
  }

  return (
    <LayoutDeAcesso tom="cidade">
      <h1 className={estilos.titulo}>Esqueci minha senha</h1>
      <p className={estilos.subtitulo}>
        Para contas de cidadão. Contas da gestão voltam pela administração.
      </p>
      <div className={estilos.avisos}>
        {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
        {etapa === 'codigo' && aviso && !falha ? <Aviso tipo="info">{aviso}</Aviso> : null}
        {etapa === 'pronto' ? (
          <Aviso tipo="sucesso" titulo="Senha nova criada">
            Por segurança, saímos de todas as sessões abertas. Entre com a nova senha.
          </Aviso>
        ) : null}
      </div>
      {etapa === 'email' && (
        <form className={estilos.formulario} onSubmit={pedirCodigo} noValidate>
          <CampoDeTexto
            rotulo="E-mail da conta"
            type="email"
            autoComplete="username"
            inputMode="email"
            spellCheck={false}
            value={email}
            onChange={(evento) => definirEmail(evento.target.value)}
          />
          <Botao type="submit" larguraTotal disabled={enviando} aria-busy={enviando}>
            {enviando ? 'Enviando...' : 'Receber o código'}
          </Botao>
        </form>
      )}
      {etapa === 'codigo' && (
        <form className={estilos.formulario} onSubmit={trocarSenha} noValidate>
          <CampoDeCodigo valor={codigo} aoMudar={definirCodigo} />
          <CampoDeSenha
            rotulo="Nova senha"
            autoComplete="new-password"
            aria-describedby={idDosRequisitos}
            value={senha}
            onChange={(evento) => definirSenha(evento.target.value)}
          />
          <ListaDeRequisitos
            id={idDosRequisitos}
            requisitos={requisitos}
            destacarPendencias={false}
          />
          <CampoDeSenha
            rotulo="Repita a nova senha"
            autoComplete="new-password"
            value={confirmacao}
            onChange={(evento) => definirConfirmacao(evento.target.value)}
          />
          <Botao type="submit" larguraTotal disabled={enviando} aria-busy={enviando}>
            {enviando ? 'Salvando...' : 'Criar a nova senha'}
          </Botao>
        </form>
      )}
      <div className={estilos.links}>
        {etapa === 'pronto' ? (
          <Link to="/entrar">Entrar com a nova senha</Link>
        ) : (
          <Link to="/entrar">Lembrei a senha: voltar para a entrada</Link>
        )}
      </div>
    </LayoutDeAcesso>
  )
}
