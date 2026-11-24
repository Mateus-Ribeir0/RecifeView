import { useState } from 'react'

import { useAcessosCorporativos, useServicoDeAcessos } from '../../../application/acessos/contexto'
import { useOrgaos } from '../../../application/encaminhamentos/useEncaminhamentos'
import {
  contarPorSituacao,
  orgaosComAcessoAtivo,
  podeReenviarConvite,
  ROTULOS_DAS_SITUACOES_DO_ACESSO,
  type AcessoCorporativo,
  type ListaDeAcessos,
  type NovoAcesso,
  type SituacaoDoAcesso,
} from '../../../domain/acessos'
import type { Orgao } from '../../../domain/encaminhamentos'
import { formatarDataEHora, formatarNumero } from '../../../domain/formatacao'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { CabecalhoDaTela } from '../../components/CabecalhoDaTela'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { GradeDeKpis } from '../../components/GradeDeKpis'
import { KpiCard } from '../../components/KpiCard'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { Tabela, type ColunaDaTabela } from '../../components/Tabela'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './Acessos.module.css'
import { FormularioDeAcesso } from './FormularioDeAcesso'

const CLASSES_DO_SELO: Readonly<Record<SituacaoDoAcesso, string>> = {
  ativo: estilos.seloAtivo ?? '',
  convite_enviado: estilos.seloConvite ?? '',
  convite_vencido: estilos.seloVencido ?? '',
  desativado: '',
}

type Edicao = { modo: 'novo' } | { modo: 'editar'; acesso: AcessoCorporativo } | null

interface AcoesProps {
  acesso: AcessoCorporativo
  aoEditar: (acesso: AcessoCorporativo) => void
  aoAgir: (acao: () => Promise<unknown>, mensagem: string) => void
}

function AcoesDoAcesso({ acesso, aoEditar, aoAgir }: AcoesProps) {
  const servico = useServicoDeAcessos()
  const [confirmando, definirConfirmando] = useState(false)
  if (confirmando) {
    return (
      <div className={estilos.acoesDaLinha}>
        <button
          type="button"
          className={`${estilos.acaoDaLinha} ${estilos.acaoPerigosa}`}
          onClick={() =>
            aoAgir(() => servico.excluir(acesso.id), `O acesso de ${acesso.nome} foi excluído.`)
          }
        >
          Confirmar exclusão
        </button>
        <button
          type="button"
          className={estilos.acaoDaLinha}
          onClick={() => definirConfirmando(false)}
        >
          Manter
        </button>
      </div>
    )
  }
  return (
    <div className={estilos.acoesDaLinha}>
      <button type="button" className={estilos.acaoDaLinha} onClick={() => aoEditar(acesso)}>
        Editar
      </button>
      {podeReenviarConvite(acesso.situacao) && (
        <button
          type="button"
          className={estilos.acaoDaLinha}
          onClick={() =>
            aoAgir(
              () => servico.reenviarConvite(acesso.id),
              `Convite novo enviado para ${acesso.email}.`,
            )
          }
        >
          Reenviar convite
        </button>
      )}
      {acesso.situacao === 'desativado' ? (
        <button
          type="button"
          className={estilos.acaoDaLinha}
          onClick={() =>
            aoAgir(() => servico.reativar(acesso.id), `${acesso.nome} pode entrar de novo.`)
          }
        >
          Reativar
        </button>
      ) : (
        <button
          type="button"
          className={estilos.acaoDaLinha}
          onClick={() =>
            aoAgir(
              () => servico.desativar(acesso.id),
              `${acesso.nome} não entra mais. As sessões abertas foram encerradas.`,
            )
          }
        >
          Desativar
        </button>
      )}
      <button
        type="button"
        className={`${estilos.acaoDaLinha} ${estilos.acaoPerigosa}`}
        onClick={() => definirConfirmando(true)}
      >
        Excluir
      </button>
    </div>
  )
}

function EmailQueQuebraNoArroba({ email }: { email: string }) {
  const arroba = email.indexOf('@')
  if (arroba < 0) return email
  return (
    <>
      {email.slice(0, arroba)}
      <wbr />
      {email.slice(arroba)}
    </>
  )
}

function colunas(
  acoes: ((acesso: AcessoCorporativo) => React.ReactNode) | null,
): ColunaDaTabela<AcessoCorporativo>[] {
  const base: ColunaDaTabela<AcessoCorporativo>[] = [
    {
      titulo: 'Responsável',
      valor: (item) => (
        <div className={estilos.responsavel}>
          <span className={estilos.nomeDoResponsavel}>{item.nome}</span>
          <span className={estilos.emailDoResponsavel}>
            <EmailQueQuebraNoArroba email={item.email} />
          </span>
        </div>
      ),
    },
    { titulo: 'Órgão', valor: (item) => item.nomeDoOrgao },
    {
      titulo: 'Situação',
      valor: (item) => (
        <span className={`${estilos.selo} ${CLASSES_DO_SELO[item.situacao]}`}>
          {ROTULOS_DAS_SITUACOES_DO_ACESSO[item.situacao]}
        </span>
      ),
    },
    {
      titulo: 'Último acesso',
      valor: (item) =>
        item.ultimoAcessoEm
          ? formatarDataEHora(item.ultimoAcessoEm)
          : item.conviteExpiraEm && item.situacao === 'convite_enviado'
            ? `convite vale até ${formatarDataEHora(item.conviteExpiraEm)}`
            : 'ainda não entrou',
    },
  ]
  return acoes ? [...base, { titulo: 'Ações', valor: acoes }] : base
}

function Indicadores({ lista, totalDeOrgaos }: { lista: ListaDeAcessos; totalDeOrgaos: number }) {
  const contagem = contarPorSituacao(lista.itens)
  return (
    <GradeDeKpis>
      <KpiCard
        rotulo="Ativos"
        valor={formatarNumero(contagem.ativo)}
        contexto="já definiram a senha"
      />
      <KpiCard
        rotulo="Convites esperando"
        valor={formatarNumero(contagem.convite_enviado)}
        contexto="enviados e ainda dentro dos 7 dias"
      />
      <KpiCard
        rotulo="Convites vencidos"
        valor={formatarNumero(contagem.convite_vencido)}
        contexto="passaram de 7 dias sem uso; reenvie"
        alerta={contagem.convite_vencido > 0}
      />
      <KpiCard
        rotulo="Órgãos com acesso ativo"
        valor={`${formatarNumero(orgaosComAcessoAtivo(lista.itens))} de ${formatarNumero(totalDeOrgaos)}`}
        contexto="os outros recebem pelo link da mensagem"
      />
    </GradeDeKpis>
  )
}

export function PaginaAcessosCorporativos() {
  useTituloDaPagina('Acessos corporativos')
  const acessos = useAcessosCorporativos()
  const { dados: orgaos } = useOrgaos()
  const servico = useServicoDeAcessos()
  const [edicao, definirEdicao] = useState<Edicao>(null)
  const [filtro, definirFiltro] = useState<Orgao | ''>('')
  const [mensagem, definirMensagem] = useState<string | null>(null)
  const [falha, definirFalha] = useState<unknown>(null)

  async function salvar(dados: NovoAcesso) {
    if (edicao?.modo === 'editar') {
      await servico.editar(edicao.acesso.id, dados)
      definirMensagem(`O acesso de ${dados.nome} foi atualizado.`)
    } else {
      await servico.criar(dados)
      definirMensagem(`Convite enviado para ${dados.email}. O link vale 7 dias.`)
    }
    definirEdicao(null)
    acessos.recarregar()
  }

  function agir(acao: () => Promise<unknown>, sucesso: string) {
    definirFalha(null)
    acao().then(
      () => {
        definirMensagem(sucesso)
        acessos.recarregar()
      },
      (motivo: unknown) => definirFalha(motivo),
    )
  }

  return (
    <div className={estilos.pagina}>
      <CabecalhoDaTela
        titulo="Acessos corporativos"
        acoes={
          acessos.dados?.podeAlterar &&
          !edicao && <Botao onClick={() => definirEdicao({ modo: 'novo' })}>Novo acesso</Botao>
        }
      >
        Quem responde, em nome de cada órgão, às ocorrências que a gestão encaminha.
      </CabecalhoDaTela>
      {mensagem && <Aviso tipo="sucesso">{mensagem}</Aviso>}
      {falha !== null && (
        <Aviso tipo="erro" titulo="A ação não foi feita">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
      {edicao && orgaos && (
        <FormularioDeAcesso
          key={edicao.modo === 'editar' ? edicao.acesso.id : 'novo'}
          orgaos={orgaos}
          editando={edicao.modo === 'editar' ? edicao.acesso : null}
          aoSalvar={salvar}
          aoCancelar={() => definirEdicao(null)}
        />
      )}
      <EstadoDaConsulta consulta={consultaDoCarregamento(acessos)}>
        {(lista) => (
          <>
            {orgaos && <Indicadores lista={lista} totalDeOrgaos={orgaos.length} />}
            {!lista.podeAlterar && (
              <Aviso tipo="info">
                Só o perfil Administração cria e altera acessos. A Gestão pública vê a lista.
              </Aviso>
            )}
            <div className={estilos.filtros}>
              <label>
                Filtrar por órgão
                <select
                  value={filtro}
                  onChange={(evento) => definirFiltro(evento.target.value as Orgao | '')}
                >
                  <option value="">Todos os órgãos</option>
                  {orgaos?.map((item) => (
                    <option key={item.orgao} value={item.orgao}>
                      {item.nome}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            {lista.itens.length === 0 ? (
              <p>Nenhum acesso corporativo criado ainda.</p>
            ) : (
              <Tabela
                legenda="Acessos corporativos"
                colunas={colunas(
                  lista.podeAlterar
                    ? (acesso) => (
                        <AcoesDoAcesso
                          acesso={acesso}
                          aoEditar={(item) => definirEdicao({ modo: 'editar', acesso: item })}
                          aoAgir={agir}
                        />
                      )
                    : null,
                )}
                linhas={lista.itens.filter((item) => !filtro || item.orgao === filtro)}
                chave={(item) => item.id}
              />
            )}
          </>
        )}
      </EstadoDaConsulta>
    </div>
  )
}
