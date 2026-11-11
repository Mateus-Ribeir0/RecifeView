import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useCatalogo } from '../../../application/consultas/usePainel'
import { useServicoDeEncaminhamentos } from '../../../application/encaminhamentos/contexto'
import { usePreparoDoEncaminhamento } from '../../../application/encaminhamentos/useEncaminhamentos'
import {
  explicarSugestao,
  ROTULOS_DOS_CANAIS,
  type Encaminhamento,
  type Orgao,
  type OrgaoDoCatalogo,
  type PreparoDoEncaminhamento,
  type SugestaoDeDestino,
} from '../../../domain/encaminhamentos'
import { formatarData, formatarNumero, formatarPorcentagem } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import { nomeDaCategoria } from '../../../domain/nomes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { consultaDoCarregamento } from '../../components/consultaDoCarregamento'
import { EstadoDaConsulta } from '../../components/EstadoDaConsulta'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Encaminhamentos.module.css'

const TAMANHO_MAXIMO_DA_JUSTIFICATIVA = 280
const ORGAOS_NA_EVIDENCIA = 4
const NOTA_DA_EVIDENCIA =
  'Fonte: indicações da Câmara Municipal (SAGL), 2021 a 2025. O órgão vem da ementa, por palavra-chave (rótulo fraco). O percentual é sobre todas as indicações do tema.'

function rotuloDoOrgao({ nome, foraDaPrefeitura, canal }: OrgaoDoCatalogo): string {
  const fora = foraDaPrefeitura ? ', fora da Prefeitura' : ''
  return `${nome}${fora} (${ROTULOS_DOS_CANAIS[canal]})`
}

function Evidencia({ sugestao }: { sugestao: SugestaoDeDestino }) {
  const nomeSugerido = sugestao.participacoes.find((item) => item.orgao === sugestao.orgao)?.nome
  return (
    <div className={estilos.sugestao}>
      <p>
        <strong>Sugestão: {nomeSugerido ?? sugestao.orgao ?? 'nenhuma'}</strong>.{' '}
        {explicarSugestao(sugestao)}
      </p>
      {sugestao.participacoes.length > 0 && (
        <>
          <ul className={estilos.participacoes} aria-label="Órgãos citados nas indicações do tema">
            {sugestao.participacoes.slice(0, ORGAOS_NA_EVIDENCIA).map((item) => (
              <li key={item.orgao}>
                <span>{item.nome}</span>
                <span
                  className={`${estilos.barra} ${item.orgao === sugestao.orgao ? estilos.barraEmFoco : ''}`}
                  style={{ width: `${Math.max(item.pct, 1)}%` }}
                  aria-hidden="true"
                />
                <span className={estilos.valor}>{formatarPorcentagem(item.pct, 1)}</span>
              </li>
            ))}
          </ul>
          <p className={estilos.nota}>
            {NOTA_DA_EVIDENCIA} n = {formatarNumero(sugestao.indicacoesDoTema)} indicações.
          </p>
        </>
      )}
    </div>
  )
}

function ResumoDaOcorrencia({ preparo }: { preparo: PreparoDoEncaminhamento }) {
  const { ocorrencia } = preparo
  const { dados: catalogo } = useCatalogo()
  const bairro = catalogo?.bairros.find((item) => item.bairroOficial === ocorrencia.bairroOficial)
  return (
    <dl className={estilos.resumoDaOcorrencia}>
      <div>
        <dt>Fonte</dt>
        <dd>{nomeDaFonte(ocorrencia.fonte)}</dd>
      </div>
      <div>
        <dt>Aberta em</dt>
        <dd>{formatarData(ocorrencia.dataAbertura)}</dd>
      </div>
      <div>
        <dt>Tema</dt>
        <dd>{nomeDaCategoria(ocorrencia.categoria)}</dd>
      </div>
      <div>
        <dt>Bairro</dt>
        <dd>{bairro?.nome ?? ocorrencia.bairroOficial ?? 'não informado'}</dd>
      </div>
      <div>
        <dt>Protocolo de origem</dt>
        <dd>{ocorrencia.protocolo ?? 'a fonte não publica'}</dd>
      </div>
    </dl>
  )
}

interface FormularioProps {
  preparo: PreparoDoEncaminhamento
  nota: number | null
  aoConcluir: (encaminhamento: Encaminhamento) => void
}

function FormularioDeEncaminhamento({ preparo, nota, aoConcluir }: FormularioProps) {
  const servico = useServicoDeEncaminhamentos()
  const id = useId()
  const [orgao, definirOrgao] = useState<Orgao | ''>(preparo.sugestao.orgao ?? '')
  const [justificativa, definirJustificativa] = useState('')
  const [enviando, definirEnviando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)
  const escolhido = preparo.orgaos.find((item) => item.orgao === orgao)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!orgao) return
    definirEnviando(true)
    definirFalha(null)
    try {
      const chaveRegistro = preparo.ocorrencia.chaveRegistro
      aoConcluir(await servico.encaminhar({ chaveRegistro, orgao, justificativa, nota }))
    } catch (motivo) {
      definirFalha(motivo)
    } finally {
      definirEnviando(false)
    }
  }

  return (
    <form onSubmit={(evento) => void enviar(evento)} className={estilos.formulario}>
      <div className={estilos.campo}>
        <label htmlFor={`${id}-orgao`}>Órgão que vai receber</label>
        <select
          id={`${id}-orgao`}
          value={orgao}
          onChange={(evento) => definirOrgao(evento.target.value as Orgao)}
          required
        >
          <option value="">Escolha o órgão</option>
          {preparo.orgaos.map((item) => (
            <option key={item.orgao} value={item.orgao}>
              {rotuloDoOrgao(item)}
            </option>
          ))}
        </select>
      </div>
      <div className={estilos.campo}>
        <label htmlFor={`${id}-justificativa`}>
          Por que encaminhar (opcional, vai na mensagem)
        </label>
        <textarea
          id={`${id}-justificativa`}
          value={justificativa}
          maxLength={TAMANHO_MAXIMO_DA_JUSTIFICATIVA}
          onChange={(evento) => definirJustificativa(evento.target.value)}
          aria-describedby={`${id}-dica`}
        />
        <p id={`${id}-dica`} className={estilos.nota}>
          Até 280 caracteres, sem CPF, telefone ou e-mail. O órgão responde por um link que vai na
          mensagem e tem 30 dias para resolver ou devolver.
        </p>
      </div>
      {falha !== null && (
        <Aviso tipo="erro" titulo="Não foi possível encaminhar">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
      <div className={estilos.acoes}>
        <Botao type="submit" disabled={!orgao || enviando}>
          {enviando ? 'Encaminhando...' : `Encaminhar${escolhido ? ` para ${escolhido.nome}` : ''}`}
        </Botao>
      </div>
    </form>
  )
}

function EncaminhamentoAberto({ preparo }: { preparo: PreparoDoEncaminhamento }) {
  const aberto = preparo.encaminhamentos[0]
  if (!aberto) return null
  return (
    <Aviso tipo="info" titulo="Esta ocorrência já está com um órgão">
      <p>
        {aberto.codigo} foi para {aberto.nomeDoOrgao}. Espere o retorno ou registre o que o órgão
        respondeu. <Link to={`/painel/encaminhamentos/${aberto.id}`}>Ver o encaminhamento</Link>
      </p>
    </Aviso>
  )
}

interface Propriedades {
  chaveRegistro: string
  nota: number | null
  aoFechar: () => void
  aoConcluir: (encaminhamento: Encaminhamento) => void
}

export function PainelDeEncaminhamento({
  chaveRegistro,
  nota,
  aoFechar,
  aoConcluir,
}: Propriedades) {
  const preparo = usePreparoDoEncaminhamento(chaveRegistro)
  const titulo = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    titulo.current?.focus()
  }, [chaveRegistro])

  return (
    <section className={estilos.painel} aria-labelledby={`titulo-${chaveRegistro}`}>
      <div className={estilos.cabecalhoDoPainel}>
        <h3 id={`titulo-${chaveRegistro}`} ref={titulo} tabIndex={-1}>
          Para quem vai esta ocorrência?
        </h3>
        <Botao variante="secundario" compacto onClick={aoFechar}>
          Fechar
        </Botao>
      </div>
      <EstadoDaConsulta consulta={consultaDoCarregamento(preparo)}>
        {(dados) => (
          <>
            <ResumoDaOcorrencia preparo={dados} />
            <Evidencia sugestao={dados.sugestao} />
            {dados.podeEncaminhar ? (
              <FormularioDeEncaminhamento preparo={dados} nota={nota} aoConcluir={aoConcluir} />
            ) : (
              <EncaminhamentoAberto preparo={dados} />
            )}
          </>
        )}
      </EstadoDaConsulta>
    </section>
  )
}
