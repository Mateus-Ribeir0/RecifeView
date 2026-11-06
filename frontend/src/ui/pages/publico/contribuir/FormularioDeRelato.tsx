import { useRef, useState, type FormEvent } from 'react'

import { useServicoDeContribuicoes } from '../../../../application/contribuicoes/contexto'
import { useCatalogoDoFormulario } from '../../../../application/contribuicoes/useFormulario'
import {
  PASSOS_DO_RELATO,
  RASCUNHO_VAZIO,
  errosDoPasso,
  gerarChaveDeEnvio,
  passoDoCampo,
  type CampoDoRelato,
  type ErrosDoRelato,
  type PassoDoRelato,
  type RascunhoDoRelato,
  type ResultadoDoEnvio,
} from '../../../../domain/contribuicoes'
import { ErroDoRecifeView } from '../../../../domain/erros'
import { Aviso } from '../../../components/Aviso'
import { Botao } from '../../../components/Botao'
import { mensagemDeFalha } from '../../../components/mensagemDeFalha'
import estilos from './FormularioDeRelato.module.css'
import { PassoEnvio } from './PassoEnvio'
import { PassoLocal } from './PassoLocal'
import { PassoServico } from './PassoServico'
import { ResultadoDoRelato } from './ResultadoDoRelato'

const ROTULOS_DOS_PASSOS: Readonly<Record<PassoDoRelato, string>> = {
  servico: 'O que aconteceu',
  local: 'Onde',
  envio: 'Enviar',
}

function Progresso({ atual }: { atual: PassoDoRelato }) {
  const posicao = PASSOS_DO_RELATO.indexOf(atual)
  return (
    <ol className={estilos.progresso} aria-label="Passos do relato">
      {PASSOS_DO_RELATO.map((passo, indice) => (
        <li
          key={passo}
          data-feito={indice < posicao || undefined}
          aria-current={indice === posicao ? 'step' : undefined}
        >
          <span className={`numero ${estilos.marcaDoPasso}`}>{indice + 1}</span>
          {ROTULOS_DOS_PASSOS[passo]}
        </li>
      ))}
    </ol>
  )
}

export function FormularioDeRelato() {
  const servico = useServicoDeContribuicoes()
  const { catalogo, erro: erroDoCatalogo } = useCatalogoDoFormulario()
  const [passo, definirPasso] = useState<PassoDoRelato>('servico')
  const [rascunho, definirRascunho] = useState<RascunhoDoRelato>(RASCUNHO_VAZIO)
  const [erros, definirErros] = useState<ErrosDoRelato>({})
  const [falha, definirFalha] = useState<unknown>(null)
  const [enviando, definirEnviando] = useState(false)
  const [resultado, definirResultado] = useState<ResultadoDoEnvio | null>(null)
  const [chaveDeEnvio, definirChaveDeEnvio] = useState(gerarChaveDeEnvio)
  const armadilha = useRef<HTMLInputElement>(null)
  const topo = useRef<HTMLDivElement>(null)

  function mudar(mudancas: Partial<RascunhoDoRelato>) {
    definirRascunho((atual) => ({ ...atual, ...mudancas }))
    definirErros({})
  }

  function irPara(destino: PassoDoRelato) {
    definirPasso(destino)
    topo.current?.scrollIntoView({ block: 'nearest' })
  }

  function avancar() {
    const encontrados = errosDoPasso(passo, rascunho)
    definirErros(encontrados)
    if (Object.keys(encontrados).length > 0) return false
    const proximo = PASSOS_DO_RELATO[PASSOS_DO_RELATO.indexOf(passo) + 1]
    if (proximo) irPara(proximo)
    return true
  }

  function voltar() {
    const anterior = PASSOS_DO_RELATO[PASSOS_DO_RELATO.indexOf(passo) - 1]
    if (anterior) irPara(anterior)
  }

  function tratarRecusa(motivo: unknown) {
    const campoRecusado = motivo instanceof ErroDoRecifeView ? motivo.campo : null
    const passoDoErro = passoDoCampo(campoRecusado)
    if (!passoDoErro || !(motivo instanceof Error)) {
      definirFalha(motivo)
      return
    }
    definirErros({ [campoRecusado as CampoDoRelato]: motivo.message })
    irPara(passoDoErro)
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    if (passo !== 'envio') {
      avancar()
      return
    }
    if (!avancar()) return
    definirEnviando(true)
    definirFalha(null)
    try {
      const recebido = await servico.enviar({
        ...rascunho,
        chaveDeEnvio,
        site: armadilha.current?.value ?? '',
      })
      definirResultado(recebido)
    } catch (motivo) {
      tratarRecusa(motivo)
    } finally {
      definirEnviando(false)
    }
  }

  function recomecar() {
    definirRascunho(RASCUNHO_VAZIO)
    definirChaveDeEnvio(gerarChaveDeEnvio())
    definirPasso('servico')
    definirResultado(null)
  }

  if (resultado) return <ResultadoDoRelato resultado={resultado} aoRecomecar={recomecar} />

  if (erroDoCatalogo) {
    return (
      <Aviso tipo="erro" titulo="O formulário não abriu">
        {mensagemDeFalha(erroDoCatalogo)}
      </Aviso>
    )
  }

  if (!catalogo) return <div className={estilos.reserva} aria-busy="true" />

  return (
    <div ref={topo} className={estilos.cartao}>
      <Progresso atual={passo} />
      <form onSubmit={(evento) => void enviar(evento)} noValidate>
        <input
          ref={armadilha}
          type="text"
          name="site"
          tabIndex={-1}
          autoComplete="off"
          aria-hidden="true"
          className={estilos.armadilha}
        />
        <div key={passo} className={estilos.passo}>
          {passo === 'servico' && (
            <PassoServico
              temas={catalogo.temas}
              escolhido={rascunho.servicoCodigo}
              erro={erros.servico}
              aoEscolher={(servicoCodigo) => mudar({ servicoCodigo })}
            />
          )}
          {passo === 'local' && (
            <PassoLocal
              bairros={catalogo.bairros}
              rascunho={rascunho}
              erros={erros}
              aoMudar={mudar}
            />
          )}
          {passo === 'envio' && <PassoEnvio rascunho={rascunho} erros={erros} aoMudar={mudar} />}
        </div>
        {falha ? (
          <Aviso tipo="erro" titulo="O relato não foi enviado">
            {mensagemDeFalha(falha)}
          </Aviso>
        ) : null}
        <div className={estilos.acoes}>
          {passo !== 'servico' && (
            <Botao type="button" variante="secundario" onClick={voltar}>
              Voltar
            </Botao>
          )}
          <Botao type="submit" disabled={enviando}>
            {passo === 'envio' ? (enviando ? 'Enviando...' : 'Enviar relato') : 'Continuar'}
          </Botao>
        </div>
      </form>
    </div>
  )
}
