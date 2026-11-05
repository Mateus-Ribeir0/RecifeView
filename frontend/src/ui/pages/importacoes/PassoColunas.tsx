import { useState } from 'react'

import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { useCamposDaBase } from '../../../application/importacoes/useHistorico'
import { formatarDataEHora } from '../../../domain/formatacao'
import { NOMES_DAS_FONTES, ORDEM_DAS_FONTES } from '../../../domain/fontes'
import type { ColunaDoArquivo, DetalheDaImportacao } from '../../../domain/importacoes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Importacoes.module.css'

const CAMPOS_OBRIGATORIOS = [
  { nome: 'data_abertura', rotulo: 'Data de abertura', aceitaValorFixo: false },
  { nome: 'categoria', rotulo: 'Categoria', aceitaValorFixo: true },
]

const ROTULOS_DA_ORIGEM: Readonly<Record<string, string>> = {
  layout: 'Layout conhecido',
  nome_igual: 'Nome igual',
  sinonimo: 'Sinônimo',
  parecido: 'Nome parecido, confira',
  sem_correspondencia: 'Sem correspondência',
  bloqueada: 'Bloqueada',
}

function usoDaColunaBloqueada(coluna: ColunaDoArquivo): string {
  if (coluna.campo === 'texto') return 'Lida só para achar o bairro da Câmara, nunca guardada'
  if (coluna.campo) return 'Vira pseudônimo do endereço e é descartada'
  return 'Descartada'
}

interface Propriedades {
  importacao: DetalheDaImportacao
  aoConcluir: () => void
  aoCancelar: () => void
}

export function PassoColunas({ importacao, aoConcluir, aoCancelar }: Propriedades) {
  const servico = useServicoDeImportacoes()
  const campos = useCamposDaBase()
  const { estrutura, decisoes } = importacao
  const [fonte, definirFonte] = useState(decisoes.fonte ?? '')
  const [dataDoRetrato, definirDataDoRetrato] = useState(decisoes.dataDoRetrato ?? '')
  const [mapeamento, definirMapeamento] = useState<Record<string, string | null>>(() =>
    Object.fromEntries(estrutura.colunas.map((coluna) => [coluna.nome, coluna.campo])),
  )
  const [valoresFixos, definirValoresFixos] = useState<Record<string, string>>({
    ...decisoes.valoresFixos,
  })
  const [enviando, definirEnviando] = useState(false)
  const [erro, definirErro] = useState<unknown>(null)
  const eDataset = importacao.layout === 'dataset'
  const camposUsados = new Set(Object.values(mapeamento))
  const faltando = CAMPOS_OBRIGATORIOS.filter(
    (campo) => !camposUsados.has(campo.nome) && !valoresFixos[campo.nome],
  )
  const conhecidos = new Set(campos.map((campo) => campo.nome))

  async function continuar() {
    definirEnviando(true)
    definirErro(null)
    try {
      await servico.definirColunas(importacao.id, {
        fonte: fonte || null,
        dataDoRetrato,
        mapeamento,
        valoresFixos,
      })
      aoConcluir()
    } catch (falha) {
      definirErro(falha)
      definirEnviando(false)
    }
  }

  return (
    <section className={estilos.passo} aria-labelledby="titulo-das-colunas">
      <h2 id="titulo-das-colunas">Confira as colunas</h2>
      <p className={estilos.subtitulo}>
        Reconhecido como: {estrutura.layoutNome ?? 'layout desconhecido'}. Formato{' '}
        {estrutura.formato ?? 'não identificado'}
        {estrutura.separador ? `, separador "${estrutura.separador}"` : ''}.
      </p>
      {estrutura.mesmoArquivo.length > 0 && (
        <Aviso tipo="alerta" titulo="Este arquivo já foi importado">
          O mesmo conteúdo entrou em{' '}
          {estrutura.mesmoArquivo.map((item) => formatarDataEHora(item.criadaEm)).join(', ')}. Você
          pode seguir: linhas iguais não são duplicadas.
        </Aviso>
      )}
      {estrutura.colunas.some((coluna) => coluna.bloqueada) && (
        <Aviso tipo="info" titulo="Colunas sensíveis foram bloqueadas">
          Os valores dessas colunas não são mostrados nem guardados, e o arquivo original será
          apagado depois da carga.
        </Aviso>
      )}
      <div className={estilos.camposDoPasso}>
        {!eDataset && (
          <label>
            De qual fonte é este arquivo?
            <select value={fonte} onChange={(evento) => definirFonte(evento.target.value)}>
              <option value="">Escolha</option>
              {ORDEM_DAS_FONTES.map((codigo) => (
                <option key={codigo} value={codigo}>
                  {NOMES_DAS_FONTES[codigo]}
                </option>
              ))}
            </select>
          </label>
        )}
        <label>
          Data do retrato (dia em que o arquivo foi baixado)
          <input
            type="date"
            value={dataDoRetrato}
            onChange={(evento) => definirDataDoRetrato(evento.target.value)}
          />
        </label>
      </div>
      <div className={estilos.rolagem}>
        <table className={estilos.tabelaDeColunas}>
          <caption className="visualmente-oculto">Colunas do arquivo e seu destino</caption>
          <thead>
            <tr>
              <th scope="col">Coluna do arquivo</th>
              <th scope="col">Exemplos</th>
              <th scope="col">Vai para</th>
              <th scope="col">Como foi reconhecida</th>
            </tr>
          </thead>
          <tbody>
            {estrutura.colunas.map((coluna) => {
              const atual = mapeamento[coluna.nome] ?? ''
              const usoInterno = Boolean(atual) && campos.length > 0 && !conhecidos.has(atual)
              return (
                <tr key={coluna.nome}>
                  <th scope="row">{coluna.nome}</th>
                  <td className={estilos.exemplos}>
                    {coluna.bloqueada
                      ? 'oculto'
                      : coluna.exemplos.join(' · ') || 'vazia na amostra'}
                  </td>
                  <td>
                    {coluna.bloqueada ? (
                      usoDaColunaBloqueada(coluna)
                    ) : usoInterno ? (
                      'Uso interno da fonte'
                    ) : (
                      <select
                        aria-label={`Destino da coluna ${coluna.nome}`}
                        value={atual}
                        onChange={(evento) =>
                          definirMapeamento((anterior) => ({
                            ...anterior,
                            [coluna.nome]: evento.target.value || null,
                          }))
                        }
                      >
                        <option value="">Ignorar</option>
                        {campos.map((campo) => (
                          <option key={campo.nome} value={campo.nome}>
                            {campo.rotulo}
                          </option>
                        ))}
                      </select>
                    )}
                  </td>
                  <td>
                    {coluna.bloqueada
                      ? `Bloqueada: ${coluna.motivoDeBloqueio ?? 'dado sensível'}`
                      : ROTULOS_DA_ORIGEM[coluna.origem]}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {faltando.length > 0 && (
        <Aviso tipo="alerta" titulo="Faltam campos obrigatórios">
          <p>
            Associe uma coluna a {faltando.map((campo) => campo.rotulo).join(' e ')} na tabela acima
            {faltando.some((campo) => campo.aceitaValorFixo)
              ? ', preencha um valor fixo abaixo ou cancele a importação.'
              : ' ou cancele a importação.'}
          </p>
          {faltando
            .filter((campo) => campo.aceitaValorFixo)
            .map((campo) => (
              <label key={campo.nome} className={estilos.valorFixo}>
                Valor fixo para {campo.rotulo}
                <input
                  type="text"
                  value={valoresFixos[campo.nome] ?? ''}
                  onChange={(evento) =>
                    definirValoresFixos((anteriores) => ({
                      ...anteriores,
                      [campo.nome]: evento.target.value,
                    }))
                  }
                />
              </label>
            ))}
        </Aviso>
      )}
      {erro ? (
        <Aviso tipo="erro" titulo="Revise as colunas">
          {mensagemDeFalha(erro)}
        </Aviso>
      ) : null}
      <div className={estilos.acoes}>
        <Botao compacto disabled={enviando || faltando.length > 0} onClick={() => void continuar()}>
          {enviando ? 'Conferindo...' : 'Conferir os dados'}
        </Botao>
        <Botao variante="secundario" compacto onClick={aoCancelar}>
          Cancelar importação
        </Botao>
      </div>
    </section>
  )
}
