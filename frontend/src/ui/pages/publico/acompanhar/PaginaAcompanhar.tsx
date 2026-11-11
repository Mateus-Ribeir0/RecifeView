import { useId, useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { useCatalogoDoFormulario } from '../../../../application/contribuicoes/useFormulario'
import { useServicoDeInformacao } from '../../../../application/informacao/contexto'
import { protocoloEValido, type AndamentoDoPedido } from '../../../../domain/pedidos'
import { Aviso } from '../../../components/Aviso'
import { Botao } from '../../../components/Botao'
import campo from '../../../components/Campo.module.css'
import { mensagemDeFalha } from '../../../components/mensagemDeFalha'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { ComparacaoDoBairro } from '../../cidade/ComparacaoDoBairro'
import { CartaoDoAndamento } from '../../pedidos/CartaoDoAndamento'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import estilos from './PaginaAcompanhar.module.css'

interface Resultado {
  protocolo: string
  andamentos: readonly AndamentoDoPedido[]
}

function SemResultado({ protocolo }: { protocolo: string }) {
  return (
    <Aviso tipo="info" titulo={`Nenhum pedido com o protocolo ${protocolo} na base`}>
      <p>
        Hoje a consulta acha os pedidos da Ouvidoria, que publica o protocolo nos dados abertos. Os
        da Central 156 e do Conecta Recife entram quando a Prefeitura ligar o sistema dela ao
        RecifeView. Confira o número ou guarde o protocolo na sua conta: ele aparece em Meus pedidos
        assim que a fonte o publicar.
      </p>
    </Aviso>
  )
}

function ConsultaPeloProtocolo() {
  const servico = useServicoDeInformacao()
  const id = useId()
  const [digitado, definirDigitado] = useState('')
  const [consultando, definirConsultando] = useState(false)
  const [resultado, definirResultado] = useState<Resultado | null>(null)
  const [falha, definirFalha] = useState<unknown>(null)
  const formatoRuim = digitado.trim() !== '' && !protocoloEValido(digitado)

  async function consultar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!protocoloEValido(digitado)) return
    definirConsultando(true)
    definirFalha(null)
    try {
      const andamentos = await servico.consultarPedido(digitado)
      definirResultado({ protocolo: digitado.trim(), andamentos })
    } catch (motivo) {
      definirFalha(motivo)
    } finally {
      definirConsultando(false)
    }
  }

  return (
    <section className={estilos.secao} aria-labelledby={`${id}-titulo`}>
      <h2 id={`${id}-titulo`}>Em que pé está o meu pedido?</h2>
      <form onSubmit={(evento) => void consultar(evento)} className={estilos.formulario}>
        <div className={campo.campo}>
          <label htmlFor={`${id}-protocolo`} className={campo.rotulo}>
            Protocolo
          </label>
          <input
            id={`${id}-protocolo`}
            className={campo.entrada}
            value={digitado}
            onChange={(evento) => definirDigitado(evento.target.value)}
            aria-invalid={formatoRuim || undefined}
            aria-describedby={`${id}-dica`}
            autoComplete="off"
          />
          <p id={`${id}-dica`} className={estilos.nota}>
            O número que você recebeu ao fazer o pedido. Letras, números, ponto, barra e hífen.
          </p>
        </div>
        <Botao type="submit" disabled={consultando || !protocoloEValido(digitado)}>
          {consultando ? 'Consultando...' : 'Consultar'}
        </Botao>
      </form>
      {falha !== null && (
        <Aviso tipo="erro" titulo="Não foi possível consultar">
          <p>{mensagemDeFalha(falha)}</p>
        </Aviso>
      )}
      {resultado && resultado.andamentos.length === 0 && (
        <SemResultado protocolo={resultado.protocolo} />
      )}
      {resultado && resultado.andamentos.length > 0 && (
        <div className={estilos.lista}>
          {resultado.andamentos.map((andamento) => (
            <CartaoDoAndamento
              key={`${andamento.fonte}-${andamento.protocolo}-${andamento.dataAbertura}`}
              andamento={andamento}
            />
          ))}
        </div>
      )}
    </section>
  )
}

function NumerosDoBairro() {
  const id = useId()
  const { catalogo } = useCatalogoDoFormulario()
  const [bairro, definirBairro] = useState('')
  return (
    <section className={estilos.secao} aria-labelledby={`${id}-titulo`}>
      <h2 id={`${id}-titulo`}>Como o meu bairro se compara com o Recife?</h2>
      <div className={campo.campo}>
        <label htmlFor={`${id}-bairro`} className={campo.rotulo}>
          Bairro
        </label>
        <select
          id={`${id}-bairro`}
          className={campo.entrada}
          value={bairro}
          onChange={(evento) => definirBairro(evento.target.value)}
        >
          <option value="">Escolha</option>
          {catalogo?.bairros.map(({ chave, nome }) => (
            <option key={chave} value={chave}>
              {nome}
            </option>
          ))}
        </select>
      </div>
      {bairro && <ComparacaoDoBairro bairro={bairro} />}
    </section>
  )
}

export function PaginaAcompanhar() {
  useTituloDaPagina('Acompanhar um pedido')

  return (
    <>
      <CabecalhoDaPagina
        rotulo="Acompanhar um pedido"
        titulo="Veja o que aconteceu com o seu pedido"
      >
        Quem recebe o pedido é o Conecta Recife, a Central 156 ou a Ouvidoria. Aqui você consulta o
        andamento pelo protocolo, vê se a gestão encaminhou o pedido a outro órgão e o que esse
        órgão respondeu. Não precisa de conta.
      </CabecalhoDaPagina>
      <div className={`conteudo ${estilos.grade}`}>
        <ConsultaPeloProtocolo />
        <aside className={estilos.lateral} aria-label="Acompanhar com uma conta">
          <h2>Acompanha mais de um pedido?</h2>
          <p>
            Com uma conta, você guarda até 20 protocolos em Meus pedidos e vê o andamento de todos
            juntos, sem digitar de novo.
          </p>
          <p>
            <Link to="/cadastrar">Criar conta</Link> ou <Link to="/entrar">entrar</Link>.
          </p>
        </aside>
        <NumerosDoBairro />
      </div>
    </>
  )
}
