import { useCallback, useId, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'

import { useCarregamento } from '../../../application/carregamento/useCarregamento'
import type { ServicoDeImportacoes } from '../../../application/importacoes/servico'
import type { ResumoDaImportacao } from '../../../domain/importacoes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import campo from '../../components/Campo.module.css'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Importacoes.module.css'

interface Propriedades {
  servico: ServicoDeImportacoes
}

function useOrigens(servico: ServicoDeImportacoes) {
  const buscar = useCallback(() => servico.origens(), [servico])
  return useCarregamento('origens', buscar)
}

function useEnvioPorOrigem() {
  const navegar = useNavigate()
  const [enviando, definirEnviando] = useState(false)
  const [erro, definirErro] = useState<unknown>(null)

  async function enviar(pedir: () => Promise<ResumoDaImportacao>) {
    definirEnviando(true)
    definirErro(null)
    try {
      const importacao = await pedir()
      await navegar(`/painel/importacoes/${importacao.id}`)
    } catch (falha) {
      definirErro(falha)
      definirEnviando(false)
    }
  }

  return { enviando, erro, enviar }
}

function FalhaDaOrigem({ erro }: { erro: unknown }) {
  if (erro === null) return null
  return (
    <Aviso tipo="erro" titulo="Os dados não foram trazidos">
      <p>{mensagemDeFalha(erro)}</p>
    </Aviso>
  )
}

export function ImportacaoPorEndereco({ servico }: Propriedades) {
  const id = useId()
  const { dados: origens } = useOrigens(servico)
  const [endereco, definirEndereco] = useState('')
  const { enviando, erro, enviar } = useEnvioPorOrigem()
  const hosts = origens?.hostsPermitidos.join(', ') ?? 'carregando'

  function baixar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    void enviar(() => servico.importarDeEndereco(endereco.trim()))
  }

  return (
    <form onSubmit={baixar} className={estilos.origem}>
      <div className={campo.campo}>
        <label htmlFor={id} className={campo.rotulo}>
          Endereço do arquivo
        </label>
        <input
          id={id}
          type="url"
          className={campo.entrada}
          value={endereco}
          placeholder="https://dados.recife.pe.gov.br/..."
          onChange={(evento) => definirEndereco(evento.target.value)}
          aria-describedby={`${id}-dica`}
        />
        <p id={`${id}-dica`} className={estilos.solturaTexto}>
          Só endereços https destes hosts: {hosts}. O arquivo da Ouvidoria do portal traz o
          protocolo de cada manifestação, que alimenta a consulta pública pelo protocolo.
        </p>
      </div>
      <FalhaDaOrigem erro={erro} />
      <div className={estilos.acoes}>
        <Botao type="submit" compacto disabled={enviando || !endereco.trim()}>
          {enviando ? 'Baixando...' : 'Baixar e analisar'}
        </Botao>
      </div>
    </form>
  )
}

export function ImportacaoPorBanco({ servico }: Propriedades) {
  const id = useId()
  const { dados: origens } = useOrigens(servico)
  const [conexao, definirConexao] = useState('')
  const [consulta, definirConsulta] = useState('')
  const { enviando, erro, enviar } = useEnvioPorOrigem()

  if (origens && origens.bancos.length === 0) {
    return (
      <Aviso tipo="info" titulo="Nenhum banco configurado">
        <p>
          As conexões ficam no servidor, em API_BANCOS_DE_ORIGEM, e nunca são digitadas aqui. Peça à
          administração para configurar a conexão de leitura com o banco da fonte.
        </p>
      </Aviso>
    )
  }

  function extrair(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    void enviar(() => servico.importarDeBanco(conexao, consulta))
  }

  return (
    <form onSubmit={extrair} className={estilos.origem}>
      <div className={campo.campo}>
        <label htmlFor={`${id}-conexao`} className={campo.rotulo}>
          Conexão
        </label>
        <select
          id={`${id}-conexao`}
          className={campo.entrada}
          value={conexao}
          onChange={(evento) => definirConexao(evento.target.value)}
        >
          <option value="">Escolha</option>
          {origens?.bancos.map((nome) => (
            <option key={nome} value={nome}>
              {nome}
            </option>
          ))}
        </select>
      </div>
      <div className={campo.campo}>
        <label htmlFor={`${id}-consulta`} className={campo.rotulo}>
          Consulta
        </label>
        <textarea
          id={`${id}-consulta`}
          className={campo.entrada}
          rows={5}
          value={consulta}
          placeholder="SELECT ... FROM ... WHERE ..."
          onChange={(evento) => definirConsulta(evento.target.value)}
          aria-describedby={`${id}-dica`}
        />
        <p id={`${id}-dica`} className={estilos.solturaTexto}>
          Só SELECT ou WITH, um comando por vez. Roda em transação só de leitura e para depois do
          tempo limite do servidor.
        </p>
      </div>
      <FalhaDaOrigem erro={erro} />
      <div className={estilos.acoes}>
        <Botao type="submit" compacto disabled={enviando || !conexao || !consulta.trim()}>
          {enviando ? 'Lendo...' : 'Ler e analisar'}
        </Botao>
      </div>
    </form>
  )
}
