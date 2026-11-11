import { useServicoDeImportacoes } from '../../../application/importacoes/contexto'
import { Abas } from '../../components/Abas'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { EnvioDeArquivo } from './EnvioDeArquivo'
import { EtapasDaImportacao } from './EtapasDaImportacao'
import { ImportacaoPorBanco, ImportacaoPorEndereco } from './ImportacaoPorOrigem'
import estilos from './Importacoes.module.css'

export function PaginaNovaImportacao() {
  useTituloDaPagina('Nova importação')
  const servico = useServicoDeImportacoes()

  return (
    <>
      <h1 className={estilos.titulo}>Nova importação</h1>
      <p className={estilos.subtitulo}>
        Traga dados novos das fontes do Recife: um arquivo, um endereço do portal de dados abertos
        ou uma consulta a um banco configurado. O RecifeView reconhece a fonte, adapta colunas e
        formatos e pergunta o que não bater antes de gravar qualquer coisa.
      </p>
      <EtapasDaImportacao atual={1} />
      <Abas
        legenda="De onde vêm os dados"
        abas={[
          { chave: 'arquivo', rotulo: 'Arquivo do computador', conteudo: <EnvioDeArquivo /> },
          {
            chave: 'endereco',
            rotulo: 'Endereço na internet',
            conteudo: <ImportacaoPorEndereco servico={servico} />,
          },
          {
            chave: 'banco',
            rotulo: 'Banco de dados',
            conteudo: <ImportacaoPorBanco servico={servico} />,
          },
        ]}
      />
      <section className={estilos.ajudaDoEnvio}>
        <h2>O que acontece com os dados</h2>
        <ul>
          <li>Nada entra na base até você confirmar a carga no último passo.</li>
          <li>
            Colunas com nome, CPF, telefone, e-mail ou texto livre são bloqueadas e os valores não
            aparecem na tela. Endereço só serve para gerar um pseudônimo e é descartado em seguida.
          </li>
          <li>
            Arquivo com esse tipo de coluna é apagado depois da carga: fica só o resultado tratado.
          </li>
          <li>
            Endereço e banco seguem o mesmo caminho do arquivo. O servidor só baixa dos endereços
            permitidos e só lê dos bancos configurados, em consulta só de leitura.
          </li>
        </ul>
      </section>
    </>
  )
}
