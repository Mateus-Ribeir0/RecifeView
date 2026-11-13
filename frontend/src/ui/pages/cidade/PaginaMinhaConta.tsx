import { useId, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useCatalogoDoFormulario } from '../../../application/contribuicoes/useFormulario'
import { mascararNome, validarNome, TAMANHO_MAXIMO_DO_NOME } from '../../../domain/conta'
import { eDaGestao } from '../../../domain/usuario'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import campo from '../../components/Campo.module.css'
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { CampoDeTexto } from '../../components/CampoDeTexto'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Cidade.module.css'

function ExcluirConta() {
  const { excluirConta } = useSessao()
  const [senha, definirSenha] = useState('')
  const [falha, definirFalha] = useState<unknown>(null)
  const [enviando, definirEnviando] = useState(false)

  async function excluir(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!senha) {
      definirFalha(new Error('Digite a sua senha para confirmar.'))
      return
    }
    definirEnviando(true)
    try {
      await excluirConta(senha)
    } catch (erro) {
      definirFalha(erro)
      definirEnviando(false)
    }
  }

  return (
    <section className={`${estilos.secaoDaConta} ${estilos.zonaDeExclusao}`}>
      <h2>Excluir a conta</h2>
      <p>
        Apagamos o seu nome, e-mail e bairro e encerramos todas as sessões. Os relatos que você
        enviou continuam, porque nunca foram ligados à conta. Não dá para desfazer.
      </p>
      {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
      <form onSubmit={excluir} className={estilos.formularioDeExclusao} noValidate>
        <CampoDeSenha
          rotulo="Sua senha"
          autoComplete="current-password"
          value={senha}
          onChange={(evento) => definirSenha(evento.target.value)}
        />
        <Botao type="submit" variante="secundario" disabled={enviando}>
          {enviando ? 'Excluindo...' : 'Excluir a minha conta'}
        </Botao>
      </form>
    </section>
  )
}

function AvisosPorEmail({ recebeAvisos }: { recebeAvisos: boolean }) {
  const { definirAvisos } = useSessao()
  const [falha, definirFalha] = useState<unknown>(null)
  const [salvando, definirSalvando] = useState(false)

  async function mudar(recebe: boolean) {
    definirSalvando(true)
    definirFalha(null)
    try {
      await definirAvisos(recebe)
    } catch (motivo) {
      definirFalha(motivo)
    } finally {
      definirSalvando(false)
    }
  }

  return (
    <section className={estilos.secaoDaConta}>
      <h2>Avisos por e-mail</h2>
      <label className={estilos.marcacaoDaConta}>
        <input
          type="checkbox"
          checked={recebeAvisos}
          disabled={salvando}
          onChange={(evento) => void mudar(evento.target.checked)}
        />
        Avisar por e-mail quando um pedido que guardei ou um relato que enviei for encaminhado,
        recebido, resolvido ou devolvido por um órgão
      </label>
      <p>O aviso traz só a etapa e o órgão, nunca o endereço nem o que você escreveu.</p>
      {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
    </section>
  )
}

export function PaginaMinhaConta() {
  useTituloDaPagina('Minha conta')
  const { estado, atualizarConta } = useSessao()
  const usuario = estado.situacao === 'autenticada' ? estado.usuario : null
  const { catalogo } = useCatalogoDoFormulario()
  const idDoBairro = useId()
  const [nome, definirNome] = useState(usuario?.nome ?? '')
  const [bairro, definirBairro] = useState(usuario?.bairroOficial ?? '')
  const [erroDoNome, definirErroDoNome] = useState<string | null>(null)
  const [falha, definirFalha] = useState<unknown>(null)
  const [salvo, definirSalvo] = useState(false)
  if (!usuario) return null

  async function salvar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const erro = validarNome(nome)
    definirErroDoNome(erro)
    if (erro) return
    definirFalha(null)
    try {
      await atualizarConta({ nome: nome.trim(), bairroOficial: bairro || null })
      definirSalvo(true)
    } catch (motivo) {
      definirFalha(motivo)
    }
  }

  return (
    <>
      <h1 className={estilos.titulo}>Minha conta</h1>
      <p className={estilos.subtitulo}>
        Guardamos só o nome, o e-mail e o bairro. Nada disso aparece para outras pessoas.
      </p>
      <form className={estilos.secaoDaConta} onSubmit={salvar} noValidate>
        <h2>Seus dados</h2>
        {salvo && <Aviso tipo="sucesso">Dados salvos.</Aviso>}
        {falha ? <Aviso tipo="erro">{mensagemDeFalha(falha)}</Aviso> : null}
        <CampoDeTexto
          rotulo="Nome"
          maxLength={TAMANHO_MAXIMO_DO_NOME}
          value={nome}
          erro={erroDoNome}
          onChange={(evento) => {
            definirNome(mascararNome(evento.target.value))
            definirSalvo(false)
          }}
        />
        <CampoDeTexto rotulo="E-mail" value={usuario.email} readOnly dica="O e-mail não muda." />
        <div className={campo.campo}>
          <label htmlFor={idDoBairro} className={campo.rotulo}>
            Seu bairro
          </label>
          <select
            id={idDoBairro}
            className={campo.entrada}
            value={bairro}
            onChange={(evento) => {
              definirBairro(evento.target.value)
              definirSalvo(false)
            }}
          >
            <option value="">Prefiro não dizer</option>
            {catalogo?.bairros.map(({ chave, nome: rotulo }) => (
              <option key={chave} value={chave}>
                {rotulo}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Botao type="submit">Salvar</Botao>
        </div>
      </form>
      <AvisosPorEmail recebeAvisos={usuario.recebeAvisos} />
      <section className={estilos.secaoDaConta}>
        <h2>Senha</h2>
        <p>
          <Link to="/definir-senha">Trocar a senha</Link>. Ao trocar, as outras sessões abertas são
          encerradas.
        </p>
      </section>
      {!eDaGestao(usuario.perfil) && <ExcluirConta />}
    </>
  )
}
