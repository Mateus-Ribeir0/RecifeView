import { useId, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { avaliarNovaSenha, novaSenhaEstaValida } from '../../../domain/senha'
import type { Usuario } from '../../../domain/usuario'
import estilos from '../../components/Acesso.module.css'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { lerEstadoDeNavegacao, ROTA_INICIAL_DO_PAINEL } from '../../components/navegacao'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { ListaDeRequisitos } from './ListaDeRequisitos'

function primeiroNome(nome: string): string {
  return nome.split(/\s+/)[0] ?? nome
}

function FormularioDeSenha({ usuario }: { usuario: Usuario }) {
  const { trocarSenha, sair } = useSessao()
  const navegar = useNavigate()
  const { destino } = lerEstadoDeNavegacao(useLocation().state)
  const idDosRequisitos = useId()
  const [senhaAtual, definirSenhaAtual] = useState('')
  const [novaSenha, definirNovaSenha] = useState('')
  const [confirmacao, definirConfirmacao] = useState('')
  const [tentouSalvar, definirTentouSalvar] = useState(false)
  const [falha, definirFalha] = useState<string | null>(null)
  const [salvando, definirSalvando] = useState(false)
  const campoAtual = useRef<HTMLInputElement>(null)
  const campoNovo = useRef<HTMLInputElement>(null)

  const obrigatoria = usuario.deveTrocarSenha
  const dados = { novaSenha, confirmacao, senhaAtual, email: usuario.email }
  const requisitos = avaliarNovaSenha(dados)
  const rotuloDaSenhaAtual = obrigatoria ? 'Senha temporária' : 'Senha atual'
  const erroDaSenhaAtual =
    tentouSalvar && !senhaAtual ? `Informe a ${rotuloDaSenhaAtual.toLowerCase()}.` : null

  async function salvar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirTentouSalvar(true)
    if (!senhaAtual) {
      campoAtual.current?.focus()
      return
    }
    if (!novaSenhaEstaValida(dados)) {
      campoNovo.current?.focus()
      return
    }
    definirFalha(null)
    definirSalvando(true)
    try {
      await trocarSenha({ senhaAtual, novaSenha })
      navegar(destino ?? ROTA_INICIAL_DO_PAINEL, { replace: true })
    } catch (erro) {
      definirFalha(mensagemDeFalha(erro))
      definirSalvando(false)
    }
  }

  return (
    <>
      <h1 className={estilos.titulo}>{obrigatoria ? 'Defina a sua senha' : 'Trocar senha'}</h1>
      <p className={estilos.subtitulo}>
        {obrigatoria
          ? `Olá, ${primeiroNome(usuario.nome)}. Por segurança, troque a senha temporária antes de usar o painel.`
          : 'Escolha uma senha nova para a sua conta.'}
      </p>
      <div className={estilos.avisos}>{falha && <Aviso tipo="erro">{falha}</Aviso>}</div>
      <form className={estilos.formulario} onSubmit={salvar} noValidate>
        <input
          type="text"
          name="usuario"
          autoComplete="username"
          value={usuario.email}
          readOnly
          hidden
        />
        <CampoDeSenha
          ref={campoAtual}
          rotulo={rotuloDaSenhaAtual}
          name="senha-atual"
          autoComplete="current-password"
          value={senhaAtual}
          onChange={(evento) => definirSenhaAtual(evento.target.value)}
          erro={erroDaSenhaAtual}
        />
        <CampoDeSenha
          ref={campoNovo}
          rotulo="Nova senha"
          name="nova-senha"
          autoComplete="new-password"
          value={novaSenha}
          onChange={(evento) => definirNovaSenha(evento.target.value)}
          aria-describedby={idDosRequisitos}
        />
        <CampoDeSenha
          rotulo="Confirme a nova senha"
          name="confirmacao"
          autoComplete="new-password"
          value={confirmacao}
          onChange={(evento) => definirConfirmacao(evento.target.value)}
        />
        <ListaDeRequisitos
          id={idDosRequisitos}
          requisitos={requisitos}
          destacarPendencias={tentouSalvar}
        />
        <Botao type="submit" larguraTotal disabled={salvando} aria-busy={salvando}>
          {salvando ? 'Salvando...' : 'Salvar senha e continuar'}
        </Botao>
      </form>
      <div className={estilos.links}>
        {obrigatoria ? (
          <button type="button" className={estilos.botaoDeLink} onClick={sair}>
            Sair sem trocar a senha
          </button>
        ) : (
          <Link to={ROTA_INICIAL_DO_PAINEL}>Cancelar e voltar ao painel</Link>
        )}
      </div>
    </>
  )
}

export function PaginaDefinirSenha() {
  useTituloDaPagina('Definir senha')
  const { estado } = useSessao()
  if (estado.situacao !== 'autenticada') return null

  return (
    <LayoutDeAcesso>
      <FormularioDeSenha usuario={estado.usuario} />
    </LayoutDeAcesso>
  )
}
