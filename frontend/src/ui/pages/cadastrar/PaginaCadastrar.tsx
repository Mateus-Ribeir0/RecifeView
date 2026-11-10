import { useId, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import {
  avaliarSenhaDoCadastro,
  codigoCompleto,
  digitosDoCodigo,
  errosDoCadastro,
  mascararNome,
  normalizarEmail,
  sugerirEmail,
  TAMANHO_MAXIMO_DO_NOME,
  type CampoDoCadastro,
  type ErrosDoCadastro,
} from '../../../domain/conta'
import { ErroDoRecifeView } from '../../../domain/erros'
import estilos from '../../components/Acesso.module.css'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import campo from '../../components/Campo.module.css'
import { CampoDeCodigo } from '../../components/CampoDeCodigo'
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { CampoDeTexto } from '../../components/CampoDeTexto'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useEsperaParaReenviar } from '../../components/useEsperaParaReenviar'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { ListaDeRequisitos } from '../definir-senha/ListaDeRequisitos'

const CAMPOS_DO_SERVIDOR: ReadonlySet<string> = new Set<CampoDoCadastro>([
  'nome',
  'termos',
  'bairro',
])

function Passos({ etapa }: { etapa: 'dados' | 'codigo' }) {
  return (
    <ol className={estilos.passos} aria-label="Passos do cadastro">
      <li
        aria-current={etapa === 'dados' ? 'step' : undefined}
        data-feito={etapa === 'codigo' || undefined}
      >
        1. Seus dados
      </li>
      <li aria-current={etapa === 'codigo' ? 'step' : undefined}>2. Confirmar o e-mail</li>
    </ol>
  )
}

function SeletorDeBairro({ valor, aoMudar }: { valor: string; aoMudar: (bairro: string) => void }) {
  const id = useId()
  const { catalogo } = useCatalogoDoFormulario()
  return (
    <div className={campo.campo}>
      <label htmlFor={id} className={campo.rotulo}>
        Seu bairro (opcional)
      </label>
      <p className={campo.dica}>Ele abre primeiro quando você entra. Dá para mudar depois.</p>
      <select
        id={id}
        className={campo.entrada}
        value={valor}
        onChange={(evento) => aoMudar(evento.target.value)}
      >
        <option value="">Prefiro não dizer</option>
        {catalogo?.bairros.map(({ chave, nome }) => (
          <option key={chave} value={chave}>
            {nome}
          </option>
        ))}
      </select>
    </div>
  )
}

interface PropriedadesDaConfirmacao {
  email: string
  senha: string
  aoVoltar: () => void
}

function EtapaDoCodigo({ email, senha, aoVoltar }: PropriedadesDaConfirmacao) {
  const { confirmarEmail, reenviarCodigo } = useSessao()
  const [codigo, definirCodigo] = useState('')
  const [falha, definirFalha] = useState<unknown>(null)
  const [aviso, definirAviso] = useState<string | null>(null)
  const [enviando, definirEnviando] = useState(false)
  const [restante, reiniciarEspera] = useEsperaParaReenviar()

  async function confirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!codigoCompleto(codigo)) {
      definirFalha(new Error('Digite os 6 dígitos do código.'))
      return
    }
    definirEnviando(true)
    definirFalha(null)
    try {
      await confirmarEmail({ email, codigo: digitosDoCodigo(codigo), senha })
    } catch (erro) {
      definirFalha(erro)
      definirEnviando(false)
    }
  }

  async function reenviar() {
    definirFalha(null)
    try {
      definirAviso(await reenviarCodigo(email))
      reiniciarEspera()
    } catch (erro) {
      definirFalha(erro)
    }
  }

  return (
    <>
      <p className={estilos.subtitulo}>
        Enviamos um código para <span className={estilos.emailDestacado}>{email}</span>. Se ele não
        chegar em alguns minutos, olhe a caixa de spam.
      </p>
      <div className={estilos.avisos}>
        {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
        {aviso && !falha ? <Aviso tipo="info">{aviso}</Aviso> : null}
      </div>
      <form className={estilos.formulario} onSubmit={confirmar} noValidate>
        <CampoDeCodigo valor={codigo} aoMudar={definirCodigo} />
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
        <button type="button" className={estilos.botaoDeLink} onClick={aoVoltar}>
          Corrigir o e-mail
        </button>
      </div>
    </>
  )
}

const DADOS_INICIAIS = {
  nome: '',
  email: '',
  senha: '',
  confirmacao: '',
  bairro: '',
  aceitouOsTermos: false,
}

export function PaginaCadastrar() {
  useTituloDaPagina('Criar conta')
  const { criarConta } = useSessao()
  const idDosRequisitos = useId()
  const armadilha = useRef<HTMLInputElement>(null)
  const [dados, definirDados] = useState(DADOS_INICIAIS)
  const [erros, definirErros] = useState<ErrosDoCadastro>({})
  const [tentouEnviar, definirTentouEnviar] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)
  const [enviando, definirEnviando] = useState(false)
  const [etapa, definirEtapa] = useState<'dados' | 'codigo'>('dados')
  const sugestao = sugerirEmail(dados.email)
  const requisitos = avaliarSenhaDoCadastro(dados)

  function mudar(mudancas: Partial<typeof DADOS_INICIAIS>) {
    definirDados((atual) => ({ ...atual, ...mudancas }))
  }

  function tratarRecusa(erro: unknown) {
    const campoRecusado = erro instanceof ErroDoRecifeView ? erro.campo : null
    if (campoRecusado && CAMPOS_DO_SERVIDOR.has(campoRecusado) && erro instanceof Error) {
      definirErros({ [campoRecusado]: erro.message })
      return
    }
    definirFalha(erro)
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirTentouEnviar(true)
    const encontrados = errosDoCadastro(dados)
    definirErros(encontrados)
    if (Object.keys(encontrados).length > 0) return
    definirEnviando(true)
    definirFalha(null)
    try {
      await criarConta({
        nome: dados.nome.trim(),
        email: normalizarEmail(dados.email),
        senha: dados.senha,
        bairroOficial: dados.bairro || null,
        aceitouOsTermos: dados.aceitouOsTermos,
        site: armadilha.current?.value ?? '',
      })
      definirEtapa('codigo')
    } catch (erro) {
      tratarRecusa(erro)
    } finally {
      definirEnviando(false)
    }
  }

  return (
    <LayoutDeAcesso tom="cidade">
      <h1 className={estilos.titulo}>Criar conta</h1>
      <Passos etapa={etapa} />
      {etapa === 'codigo' ? (
        <EtapaDoCodigo
          email={normalizarEmail(dados.email)}
          senha={dados.senha}
          aoVoltar={() => definirEtapa('dados')}
        />
      ) : (
        <>
          <p className={estilos.subtitulo}>
            Com a conta, você acompanha os relatos da cidade e os números do seu bairro. Não pedimos
            CPF nem telefone.
          </p>
          <div className={estilos.avisos}>
            {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
          </div>
          <form className={estilos.formulario} onSubmit={enviar} noValidate>
            <input
              ref={armadilha}
              type="text"
              name="site"
              tabIndex={-1}
              autoComplete="off"
              aria-hidden="true"
              className={estilos.armadilha}
            />
            <CampoDeTexto
              rotulo="Nome"
              autoComplete="name"
              maxLength={TAMANHO_MAXIMO_DO_NOME}
              value={dados.nome}
              erro={erros.nome}
              onChange={(evento) => mudar({ nome: mascararNome(evento.target.value) })}
            />
            <div className={estilos.campoDeEscolha}>
              <CampoDeTexto
                rotulo="E-mail"
                type="email"
                autoComplete="email"
                inputMode="email"
                spellCheck={false}
                value={dados.email}
                erro={erros.email}
                onChange={(evento) => mudar({ email: evento.target.value })}
                onBlur={() => mudar({ email: normalizarEmail(dados.email) })}
              />
              {sugestao && (
                <p className={estilos.sugestao} role="status">
                  Você quis dizer <strong>{sugestao}</strong>?{' '}
                  <button
                    type="button"
                    className={estilos.botaoDeLink}
                    onClick={() => mudar({ email: sugestao })}
                  >
                    Usar este
                  </button>
                </p>
              )}
            </div>
            <SeletorDeBairro valor={dados.bairro} aoMudar={(bairro) => mudar({ bairro })} />
            <CampoDeSenha
              rotulo="Senha"
              autoComplete="new-password"
              aria-describedby={idDosRequisitos}
              value={dados.senha}
              erro={erros.senha}
              onChange={(evento) => mudar({ senha: evento.target.value })}
            />
            <ListaDeRequisitos
              id={idDosRequisitos}
              requisitos={requisitos}
              destacarPendencias={tentouEnviar}
            />
            <CampoDeSenha
              rotulo="Repita a senha"
              autoComplete="new-password"
              value={dados.confirmacao}
              erro={erros.confirmacao}
              onChange={(evento) => mudar({ confirmacao: evento.target.value })}
            />
            <div className={estilos.campoDeEscolha}>
              <label className={estilos.aceite}>
                <input
                  type="checkbox"
                  checked={dados.aceitouOsTermos}
                  aria-invalid={erros.termos ? true : undefined}
                  onChange={(evento) => mudar({ aceitouOsTermos: evento.target.checked })}
                />
                <span>
                  Li{' '}
                  <a href="/como-funciona#privacidade" target="_blank" rel="noopener">
                    como o RecifeView usa os meus dados
                  </a>{' '}
                  e aceito. Guardamos só nome, e-mail e bairro, e você pode excluir a conta quando
                  quiser.
                </span>
              </label>
              {erros.termos && <p className={campo.erro}>{erros.termos}</p>}
            </div>
            <Botao type="submit" larguraTotal disabled={enviando} aria-busy={enviando}>
              {enviando ? 'Enviando...' : 'Criar conta e receber o código'}
            </Botao>
          </form>
          <div className={estilos.links}>
            <p>
              Já tem conta? <Link to="/entrar">Entrar</Link>
            </p>
            <Link to="/">Voltar para a página inicial</Link>
          </div>
        </>
      )}
    </LayoutDeAcesso>
  )
}
