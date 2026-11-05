import { useState } from 'react'

import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { formatarData, formatarNumero } from '../../../domain/formatacao'
import { nomeDaFonte } from '../../../domain/fontes'
import type { DetalheDaImportacao, PreviaDeLinha } from '../../../domain/importacoes'
import { Aviso } from '../../components/Aviso'
import { Botao } from '../../components/Botao'
import { mensagemDeFalha } from '../../components/mensagemDeFalha'
import estilos from './Importacoes.module.css'
import { ResumoEmNumeros } from './ResumoEmNumeros'

const CAMPOS_DA_PREVIA: readonly (readonly [string, string])[] = [
  ['data_abertura', 'Abertura'],
  ['categoria', 'Categoria'],
  ['servico', 'Serviço'],
  ['bairro_oficial', 'Bairro'],
  ['rpa', 'RPA'],
  ['situacao', 'Situação'],
  ['dias_ate_movimento', 'Dias'],
]

function valorNaBase(campo: string, valor: string | null | undefined): string {
  if (!valor) return 'sem dado'
  return campo === 'data_abertura' ? formatarData(valor) : valor
}

interface PropriedadesDaPrevia {
  previa: readonly PreviaDeLinha[]
  colunasDoArquivo: readonly string[]
}

function PreviaAntesEDepois({ previa, colunasDoArquivo }: PropriedadesDaPrevia) {
  const visiveis = previa[0]?.antes ?? {}
  const colunas = colunasDoArquivo.filter((coluna) => coluna in visiveis)
  return (
    <div className={estilos.previa}>
      <div className={estilos.rolagem}>
        <h3>Como veio no arquivo</h3>
        <table className={estilos.tabelaDeColunas}>
          <thead>
            <tr>
              {colunas.map((coluna) => (
                <th key={coluna} scope="col">
                  {coluna}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {previa.map((linha, indice) => (
              <tr key={indice}>
                {colunas.map((coluna) => (
                  <td key={coluna}>{linha.antes[coluna]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className={estilos.rolagem}>
        <h3>Como vai ficar na base</h3>
        <table className={estilos.tabelaDeColunas}>
          <thead>
            <tr>
              {CAMPOS_DA_PREVIA.map(([campo, rotulo]) => (
                <th key={campo} scope="col">
                  {rotulo}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {previa.map((linha, indice) => (
              <tr key={indice}>
                {CAMPOS_DA_PREVIA.map(([campo]) => (
                  <td key={campo}>{valorNaBase(campo, linha.depois[campo])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

interface Propriedades {
  importacao: DetalheDaImportacao
  aoConcluir: () => void
  aoCancelar: () => void
}

export function PassoRevisao({ importacao, aoConcluir, aoCancelar }: Propriedades) {
  const servico = useServicoDeImportacoes()
  const { resumo, previa } = importacao.pendencias
  const [enviando, definirEnviando] = useState(false)
  const [erro, definirErro] = useState<unknown>(null)
  const descartadas = resumo.lidas - resumo.aceitas
  const fontes = Object.keys(resumo.fontes).map(nomeDaFonte).join(', ')
  const novasDecisao = importacao.decisoes.repetidosNaBase

  async function confirmar() {
    definirEnviando(true)
    definirErro(null)
    try {
      await servico.confirmar(importacao.id)
      aoConcluir()
    } catch (falha) {
      definirErro(falha)
      definirEnviando(false)
    }
  }

  return (
    <section className={estilos.passo} aria-labelledby="titulo-da-revisao">
      <h2 id="titulo-da-revisao">Revise antes de gravar</h2>
      <p className={estilos.subtitulo}>
        {fontes || 'Sem fonte identificada'}, de {formatarData(resumo.periodoInicio)} a{' '}
        {formatarData(resumo.periodoFim)}. Retrato de {formatarData(importacao.dataDoRetrato)}.
      </p>
      <ResumoEmNumeros
        numeros={[
          { rotulo: 'Linhas lidas', valor: resumo.lidas },
          { rotulo: 'Entram como novas', valor: resumo.novas },
          {
            rotulo: 'Já existem com outros dados',
            valor: resumo.alteradas,
            contexto: novasDecisao === 'atualizar' ? 'serão atualizadas' : 'não mudam',
          },
          { rotulo: 'Idênticas à base', valor: resumo.iguais, contexto: 'não mudam nada' },
          { rotulo: 'Descartadas', valor: descartadas },
        ]}
        descartes={resumo.descartes}
        correcoes={resumo.correcoes}
      />
      {resumo.semIdLocal > 0 && (
        <Aviso tipo="alerta" titulo="Registros fora da reincidência">
          O sal do pseudônimo de endereço não está configurado nesta instalação.{' '}
          {formatarNumero(resumo.semIdLocal)} registros entram sem pseudônimo: contam em tudo, menos
          na reincidência.
        </Aviso>
      )}
      {previa.length > 0 && (
        <PreviaAntesEDepois
          previa={previa}
          colunasDoArquivo={importacao.estrutura.colunas.map((coluna) => coluna.nome)}
        />
      )}
      {erro ? (
        <Aviso tipo="erro" titulo="A carga não começou">
          {mensagemDeFalha(erro)}
        </Aviso>
      ) : null}
      <div className={estilos.acoes}>
        <Botao compacto disabled={enviando} onClick={() => void confirmar()}>
          {enviando ? 'Iniciando...' : 'Confirmar a carga'}
        </Botao>
        <Botao variante="secundario" compacto onClick={aoCancelar}>
          Cancelar importação
        </Botao>
      </div>
    </section>
  )
}
