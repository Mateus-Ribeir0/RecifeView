import { useId, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import {
  avaliarSenhaDoCadastro,
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
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { CampoDeTexto } from '../../components/CampoDeTexto'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { ListaDeRequisitos } from '../definir-senha/ListaDeRequisitos'

const CAMPOS_DO_SERVIDOR: ReadonlySet<string> = new Set<CampoDoCadastro>([
  'nome',
  'email',
  'termos',
  'bairro',
])

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
    } catch (erro) {
      tratarRecusa(erro)
      definirEnviando(false)
    }
  }

  return (
    <LayoutDeAcesso tom="cidade">
      <h1 className={estilos.titulo}>Criar conta</h1>
      <p className={estilos.subtitulo}>
        Com a conta, você acompanha os relatos da cidade e os números do seu bairro. Não pedimos CPF
        nem telefone.
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
          {enviando ? 'Criando a conta...' : 'Criar conta e entrar'}
        </Botao>
      </form>
      <div className={estilos.links}>
        <p>
          Já tem conta? <Link to="/entrar">Entrar</Link>
        </p>
        <Link to="/">Voltar para a página inicial</Link>
      </div>
    </LayoutDeAcesso>
  )
}
