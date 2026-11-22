import { useCallback, useId, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useCarregamento } from '../../../application/carregamento/useCarregamento'
import type { ConviteDeAcesso } from '../../../domain/acessos'
import { formatarDataEHora } from '../../../domain/formatacao'
import { avaliarPrimeiraSenha } from '../../../domain/senha'
import { ROTA_INICIAL_CORPORATIVA } from '../../../domain/usuario'
import estilos from '../../components/Acesso.module.css'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CampoDeSenha } from '../../components/CampoDeSenha'
import { LayoutDeAcesso } from '../../components/LayoutDeAcesso'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { ListaDeRequisitos } from '../definir-senha/ListaDeRequisitos'

function FormularioDoConvite({ token, convite }: { token: string; convite: ConviteDeAcesso }) {
  const { aceitarConvite } = useSessao()
  const navegar = useNavigate()
  const idDosRequisitos = useId()
  const campo = useRef<HTMLInputElement>(null)
  const [senha, definirSenha] = useState('')
  const [confirmacao, definirConfirmacao] = useState('')
  const [tentou, definirTentou] = useState(false)
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<string | null>(null)
  const requisitos = avaliarPrimeiraSenha({ novaSenha: senha, confirmacao, email: convite.email })

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirTentou(true)
    if (!requisitos.every((requisito) => requisito.atendido)) {
      campo.current?.focus()
      return
    }
    definirEnviando(true)
    definirFalha(null)
    try {
      await aceitarConvite({ token, senha })
      navegar(ROTA_INICIAL_CORPORATIVA, { replace: true })
    } catch (erro) {
      definirFalha(mensagemDeFalha(erro))
      definirEnviando(false)
    }
  }

  return (
    <>
      <h1 className={estilos.titulo}>Defina a sua senha</h1>
      <p className={estilos.subtitulo}>
        {convite.nome}, este é o seu acesso de <strong>{convite.nomeDoOrgao}</strong> no RecifeView.
        O convite vale até {formatarDataEHora(convite.expiraEm)} e pode ser usado uma vez.
      </p>
      <div className={estilos.avisos}>{falha && <Aviso tipo="erro">{falha}</Aviso>}</div>
      <form className={estilos.formulario} onSubmit={(evento) => void enviar(evento)} noValidate>
        <input
          type="text"
          name="usuario"
          autoComplete="username"
          value={convite.email}
          readOnly
          hidden
        />
        <CampoDeSenha
          ref={campo}
          rotulo="Senha"
          name="nova-senha"
          autoComplete="new-password"
          value={senha}
          onChange={(evento) => definirSenha(evento.target.value)}
          aria-describedby={idDosRequisitos}
        />
        <CampoDeSenha
          rotulo="Confirme a senha"
          name="confirmacao"
          autoComplete="new-password"
          value={confirmacao}
          onChange={(evento) => definirConfirmacao(evento.target.value)}
        />
        <ListaDeRequisitos
          id={idDosRequisitos}
          requisitos={requisitos}
          destacarPendencias={tentou}
        />
        <Botao type="submit" larguraTotal disabled={enviando} aria-busy={enviando}>
          {enviando ? 'Entrando...' : 'Salvar senha e entrar'}
        </Botao>
      </form>
      <div className={estilos.links}>
        <p className={estilos.chamadaDeCadastro}>
          O acesso fica com <strong>{convite.email}</strong>. Nas próximas vezes, entre pela área
          corporativa.
        </p>
        <Link to="/entrar/corporativo">Ir para a entrada da área corporativa</Link>
      </div>
    </>
  )
}

function ConviteIndisponivel({ falha }: { falha: unknown }) {
  return (
    <>
      <h1 className={estilos.titulo}>Este convite não vale mais</h1>
      <div className={estilos.avisos}>
        <Aviso tipo="alerta">{mensagemDeFalha(falha)}</Aviso>
      </div>
      <div className={estilos.links}>
        <Link to="/entrar/corporativo">Já definiu a senha? Entre pela área corporativa</Link>
        <Link to="/recuperar-senha">Esqueci minha senha</Link>
      </div>
    </>
  )
}

export function PaginaConvite() {
  useTituloDaPagina('Convite para a área corporativa')
  const { token = '' } = useParams()
  const { abrirConvite } = useSessao()
  const buscar = useCallback(() => abrirConvite(token), [abrirConvite, token])
  const convite = useCarregamento(`convite-${token}`, buscar)

  return (
    <LayoutDeAcesso tom="corporativo">
      {convite.carregando && <p className={estilos.subtitulo}>Conferindo o convite...</p>}
      {convite.erro !== null && <ConviteIndisponivel falha={convite.erro} />}
      {convite.dados && <FormularioDoConvite token={token} convite={convite.dados} />}
    </LayoutDeAcesso>
  )
}
