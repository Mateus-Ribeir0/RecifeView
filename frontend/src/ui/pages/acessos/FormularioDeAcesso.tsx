import { useId, useState, type FormEvent } from 'react'

import type { AcessoCorporativo, NovoAcesso } from '../../../domain/acessos'
import { pareceEmail } from '../../../domain/acesso'
import type { Orgao, OrgaoDoCatalogo } from '../../../domain/encaminhamentos'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CampoDeTexto } from '../../components/CampoDeTexto'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Acessos.module.css'

interface Propriedades {
  orgaos: readonly OrgaoDoCatalogo[]
  editando: AcessoCorporativo | null
  aoSalvar: (dados: NovoAcesso) => Promise<void>
  aoCancelar: () => void
}

/** Na edição, o e-mail fica fixo: ele é o acesso. Para outro e-mail, crie outro acesso. */
export function FormularioDeAcesso({ orgaos, editando, aoSalvar, aoCancelar }: Propriedades) {
  const id = useId()
  const [nome, definirNome] = useState(editando?.nome ?? '')
  const [email, definirEmail] = useState(editando?.email ?? '')
  const [orgao, definirOrgao] = useState<Orgao | ''>(editando?.orgao ?? '')
  const [tentou, definirTentou] = useState(false)
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)
  const erros = {
    nome: nome.trim().length < 2 ? 'Informe o nome de quem vai responder pelo órgão.' : null,
    email: !editando && !pareceEmail(email) ? 'Informe um e-mail válido.' : null,
    orgao: orgao ? null : 'Escolha o órgão.',
  }

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirTentou(true)
    if (erros.nome || erros.email || !orgao) return
    definirEnviando(true)
    definirFalha(null)
    try {
      await aoSalvar({ nome, email, orgao })
    } catch (motivo) {
      definirFalha(motivo)
      definirEnviando(false)
    }
  }

  return (
    <form className={estilos.formulario} onSubmit={(evento) => void enviar(evento)} noValidate>
      <h3>{editando ? `Editar o acesso de ${editando.nome}` : 'Novo acesso corporativo'}</h3>
      <div className={estilos.campos}>
        <CampoDeTexto
          rotulo="Nome do responsável"
          value={nome}
          onChange={(evento) => definirNome(evento.target.value)}
          erro={tentou ? erros.nome : null}
          autoComplete="off"
        />
        <CampoDeTexto
          rotulo="E-mail do responsável"
          type="email"
          value={email}
          disabled={Boolean(editando)}
          onChange={(evento) => definirEmail(evento.target.value)}
          erro={tentou ? erros.email : null}
          dica={
            editando
              ? 'O e-mail não muda: é com ele que a pessoa entra.'
              : 'O convite vai para este e-mail.'
          }
          autoComplete="off"
        />
        <div className={estilos.campo}>
          <label htmlFor={`${id}-orgao`}>Órgão</label>
          <select
            id={`${id}-orgao`}
            value={orgao}
            onChange={(evento) => definirOrgao(evento.target.value as Orgao)}
            aria-invalid={tentou && Boolean(erros.orgao)}
          >
            <option value="">Escolha o órgão</option>
            {orgaos.map((item) => (
              <option key={item.orgao} value={item.orgao}>
                {item.nome}
                {item.foraDaPrefeitura ? ', fora da Prefeitura' : ''}
              </option>
            ))}
          </select>
          {tentou && erros.orgao && <p className={estilos.erro}>{erros.orgao}</p>}
        </div>
      </div>
      {!editando && (
        <p className={estilos.nota}>
          A pessoa recebe um link de uso único, válido por 7 dias, para definir a senha. Ninguém da
          administração vê essa senha.
        </p>
      )}
      {falha !== null && (
        <Aviso tipo="erro" titulo="O acesso não foi salvo">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
      <div className={estilos.acoes}>
        <Botao type="submit" disabled={enviando}>
          {enviando ? 'Salvando...' : editando ? 'Salvar alterações' : 'Criar e mandar o convite'}
        </Botao>
        <Botao type="button" variante="secundario" onClick={aoCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  )
}
