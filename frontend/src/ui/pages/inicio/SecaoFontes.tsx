import { formatarNumero } from '../../../domain/formatacao'
import { FONTES_DE_DADOS } from './conteudo'
import secao from './Secao.module.css'
import estilos from './SecaoFontes.module.css'

const TOTAL_DE_REGISTROS = FONTES_DE_DADOS.reduce((total, fonte) => total + fonte.registros, 0)

export function SecaoFontes() {
  return (
    <section id="fontes" className={secao.secao} aria-labelledby="titulo-fontes">
      <div className="conteudo">
        <p className={secao.rotulo}>Fontes</p>
        <h2 id="titulo-fontes" className={secao.titulo}>
          De onde vêm os dados
        </h2>
        <p className={secao.abertura}>
          Só bases públicas, do município do Recife. Nenhuma chave liga o registro de uma fonte ao
          de outra: o cruzamento é feito por bairro, serviço e período.
        </p>
        <div className={estilos.rolagem} tabIndex={0} aria-label="Tabela das fontes de dados">
          <table className={estilos.tabela}>
            <caption className="visualmente-oculto">
              Fontes do dataset RecifeView 1.0, com o período e a quantidade de registros
            </caption>
            <thead>
              <tr>
                <th scope="col">Fonte</th>
                <th scope="col">O que cada registro representa</th>
                <th scope="col">Período</th>
                <th scope="col" className={estilos.numerica}>
                  Registros
                </th>
              </tr>
            </thead>
            <tbody>
              {FONTES_DE_DADOS.map(({ nome, registra, periodo, registros }) => (
                <tr key={nome}>
                  <th scope="row">{nome}</th>
                  <td>{registra}</td>
                  <td>{periodo}</td>
                  <td className={`numero ${estilos.numerica}`}>{formatarNumero(registros)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th scope="row" colSpan={3}>
                  Total
                </th>
                <td className={`numero ${estilos.numerica}`}>
                  {formatarNumero(TOTAL_DE_REGISTROS)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
        <div className={estilos.privacidade}>
          <h3>Privacidade</h3>
          <ul>
            <li>Nome, CPF, telefone, e-mail e endereço completo foram removidos.</li>
            <li>
              O endereço virou um código que não pode ser revertido sem um segredo guardado fora do
              projeto.
            </li>
            <li>As coordenadas foram arredondadas para cerca de 100 metros.</li>
            <li>O texto dos chamados em área de risco nunca é publicado.</li>
          </ul>
        </div>
        <p className={`${secao.nota} ${estilos.nota}`}>
          Fonte: Portal de Dados Abertos do Recife (licença ODbL), sistema SAGL da Câmara Municipal
          do Recife e Censo 2022 do IBGE. A SEDEC vem da cópia de 09/03/2024 guardada pelo Internet
          Archive.
        </p>
      </div>
    </section>
  )
}
