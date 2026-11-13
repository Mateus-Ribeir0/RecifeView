import { useId, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useSessao } from '../../../application/autenticacao/useSessao'
import { useServicoDeInformacao } from '../../../application/informacao/contexto'
import { useMeusPedidos } from '../../../application/informacao/useInformacao'
import { formatarData } from '../../../domain/formatacao'
import { protocoloEValido, type PedidoAcompanhado } from '../../../domain/pedidos'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import campo from '../../components/Campo.module.css'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { CartaoDoAndamento } from '../pedidos/CartaoDoAndamento'
import estilos from '../pedidos/Pedidos.module.css'
import cidade from './Cidade.module.css'

function NovoPedido({ aoGuardar }: { aoGuardar: () => void }) {
  const servico = useServicoDeInformacao()
  const id = useId()
  const [digitado, definirDigitado] = useState('')
  const [guardando, definirGuardando] = useState(false)
  const [falha, definirFalha] = useState<unknown>(null)

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirGuardando(true)
    definirFalha(null)
    try {
      await servico.acompanharPedido(digitado)
      definirDigitado('')
      aoGuardar()
    } catch (motivo) {
      definirFalha(motivo)
    } finally {
      definirGuardando(false)
    }
  }

  return (
    <>
      <form onSubmit={(evento) => void guardar(evento)} className={estilos.formulario}>
        <div className={campo.campo}>
          <label htmlFor={id} className={campo.rotulo}>
            Protocolo do pedido
          </label>
          <input
            id={id}
            className={campo.entrada}
            value={digitado}
            onChange={(evento) => definirDigitado(evento.target.value)}
            autoComplete="off"
          />
        </div>
        <Botao type="submit" disabled={guardando || !protocoloEValido(digitado)}>
          {guardando ? 'Guardando...' : 'Acompanhar'}
        </Botao>
      </form>
      {falha !== null && (
        <Aviso tipo="erro" titulo="Não foi possível guardar o protocolo">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
    </>
  )
}

function Pedido({ pedido, aoTirar }: { pedido: PedidoAcompanhado; aoTirar: () => void }) {
  const servico = useServicoDeInformacao()
  const [tirando, definirTirando] = useState(false)

  async function tirar() {
    definirTirando(true)
    await servico.deixarDeAcompanhar(pedido.id)
    aoTirar()
  }

  return (
    <li className={estilos.pedido}>
      <div className={estilos.cabecalhoDoPedido}>
        <p className={estilos.fonte}>
          Protocolo {pedido.protocolo}, guardado em {formatarData(pedido.criadoEm)}
        </p>
        <Botao variante="secundario" compacto disabled={tirando} onClick={() => void tirar()}>
          Deixar de acompanhar
        </Botao>
      </div>
      {pedido.andamentos.length === 0 ? (
        <p className={estilos.nota}>
          Ainda sem registro na base. O protocolo fica guardado e o andamento aparece aqui quando a
          fonte publicar o pedido.
        </p>
      ) : (
        pedido.andamentos.map((andamento) => (
          <CartaoDoAndamento
            key={`${andamento.fonte}-${andamento.dataAbertura}`}
            andamento={andamento}
          />
        ))
      )}
    </li>
  )
}

function SituacaoDosAvisos() {
  const { estado } = useSessao()
  const recebe = estado.situacao === 'autenticada' && estado.usuario.recebeAvisos
  return (
    <p className={estilos.nota}>
      {recebe
        ? 'Você recebe um e-mail quando um pedido daqui muda de etapa. '
        : 'Os avisos por e-mail estão desligados. '}
      <Link to="/cidade/conta">Mudar em Minha conta</Link>
    </p>
  )
}

export function PaginaMeusPedidos() {
  useTituloDaPagina('Meus pedidos')
  const pedidos = useMeusPedidos()

  return (
    <>
      <h1 className={cidade.titulo}>Meus pedidos</h1>
      <p className={cidade.subtitulo}>
        Guarde o protocolo dos pedidos que você fez no Conecta Recife, na Central 156 ou na
        Ouvidoria. Aqui aparece a situação de cada um e, se a gestão encaminhou o pedido a outro
        órgão, a resposta desse órgão. Até 20 protocolos por conta.
      </p>
      <SituacaoDosAvisos />
      <NovoPedido aoGuardar={pedidos.recarregar} />
      {pedidos.erro !== null && (
        <Aviso tipo="erro" titulo="Não foi possível carregar os seus pedidos">
          <p>{mensagemDeFalha(pedidos.erro)}</p>
        </Aviso>
      )}
      {pedidos.dados?.length === 0 && (
        <p className={estilos.nota}>Nenhum protocolo guardado ainda.</p>
      )}
      {pedidos.dados && pedidos.dados.length > 0 && (
        <ul className={estilos.lista}>
          {pedidos.dados.map((pedido) => (
            <Pedido key={pedido.id} pedido={pedido} aoTirar={pedidos.recarregar} />
          ))}
        </ul>
      )}
    </>
  )
}
