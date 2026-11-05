import { contar, formatarNumero } from '../../../domain/formatacao'
import {
  ACEITAR_COMO_NOVO,
  DEIXAR_VAZIO,
  DESCARTAR_LINHA,
  type Pendencia,
} from '../../../domain/importacoes'
import { nomeDaCategoria, nomeDoOrgao } from '../../../domain/nomes'
import estilos from './Importacoes.module.css'

interface Propriedades {
  pendencia: Pendencia
  escolhas: Readonly<Record<string, string>>
  padrao: string
  aoEscolher: (valor: string, escolha: string) => void
  aoEscolherPadrao: (escolha: string) => void
}

function rotuloDaAlternativa(campo: string | null, alternativa: string): string {
  if (campo === 'categoria' || campo === 'bairro') return nomeDaCategoria(alternativa)
  return campo === 'orgao' ? nomeDoOrgao(alternativa) : alternativa
}

function OpcoesFixas({ eBairro }: { eBairro: boolean }) {
  return (
    <>
      {eBairro ? (
        <option value={DEIXAR_VAZIO}>Deixar sem bairro</option>
      ) : (
        <option value={ACEITAR_COMO_NOVO}>Aceitar como novo</option>
      )}
      <option value={DESCARTAR_LINHA}>Descartar estas linhas</option>
    </>
  )
}

export function ValoresEmDuvida({
  pendencia,
  escolhas,
  padrao,
  aoEscolher,
  aoEscolherPadrao,
}: Propriedades) {
  const eBairro = pendencia.tipo === 'bairro_desconhecido'
  const titulo = eBairro
    ? 'Bairros que não estão entre os 94 oficiais'
    : `Valores novos em ${pendencia.rotuloDoCampo ?? pendencia.campo}`
  const restam = pendencia.totalDeValores - pendencia.valores.length

  return (
    <fieldset className={estilos.pergunta}>
      <legend>{titulo}</legend>
      <p className={estilos.textoDaPergunta}>
        {contar(pendencia.quantidade, 'linha tem', 'linhas têm')}{' '}
        {contar(pendencia.totalDeValores, 'valor', 'valores')} que a base ainda não conhece. Para
        cada um, escolha o que fazer.
      </p>
      <div className={estilos.rolagemDosValores}>
        <table className={estilos.tabelaDeColunas}>
          <caption className="visualmente-oculto">{titulo}</caption>
          <thead>
            <tr>
              <th scope="col">Valor no arquivo</th>
              <th scope="col">Linhas</th>
              <th scope="col">O que fazer</th>
            </tr>
          </thead>
          <tbody>
            {pendencia.valores.map((item) => (
              <tr key={item.valor}>
                <th scope="row">{item.valor}</th>
                <td className="numero">{formatarNumero(item.quantidade)}</td>
                <td>
                  <select
                    aria-label={`O que fazer com ${item.valor}`}
                    value={escolhas[item.valor] ?? ''}
                    onChange={(evento) => aoEscolher(item.valor, evento.target.value)}
                  >
                    <option value="">Escolha</option>
                    <OpcoesFixas eBairro={eBairro} />
                    <optgroup
                      label={eBairro ? 'Associar ao bairro' : 'Associar a um valor conhecido'}
                    >
                      {pendencia.alternativas.map((alternativa) => (
                        <option key={alternativa} value={alternativa}>
                          {rotuloDaAlternativa(pendencia.campo, alternativa)}
                        </option>
                      ))}
                    </optgroup>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <label className={estilos.valorFixo}>
        {restam > 0
          ? `Para os outros ${formatarNumero(restam)} valores e os que ficarem sem escolha`
          : 'Para os valores que ficarem sem escolha'}
        <select value={padrao} onChange={(evento) => aoEscolherPadrao(evento.target.value)}>
          <option value="">Perguntar de novo</option>
          <OpcoesFixas eBairro={eBairro} />
        </select>
      </label>
    </fieldset>
  )
}
