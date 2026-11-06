import { Aparecer } from '../../../components/Aparecer'
import { Icone, type NomeDoIcone } from '../../../components/Icone'
import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { CabecalhoDaPagina } from '../CabecalhoDaPagina'
import { FormularioDeRelato } from './FormularioDeRelato'
import estilos from './PaginaContribuir.module.css'

const CAMINHO_DO_RELATO: readonly { icone: NomeDoIcone; titulo: string; texto: string }[] = [
  {
    icone: 'relato',
    titulo: 'Você envia',
    texto: 'Sem nome, CPF, telefone ou e-mail.',
  },
  {
    icone: 'somar',
    titulo: 'A plataforma confere',
    texto: 'Se outra pessoa já relatou o mesmo problema, os relatos viram uma ocorrência só.',
  },
  {
    icone: 'pessoas',
    titulo: 'A gestão revisa',
    texto: 'Nada entra no painel sem passar por uma pessoa.',
  },
  {
    icone: 'telas',
    titulo: 'Entra na análise',
    texto: 'O relato passa a contar nos indicadores do bairro e do serviço.',
  },
]

export function PaginaContribuir() {
  useTituloDaPagina('Relatar um problema')

  return (
    <>
      <CabecalhoDaPagina rotulo="Relatar um problema" titulo="Conte o que está acontecendo na rua">
        Leva um minuto e não pede os seus dados. Se o problema já foi relatado, o seu relato reforça
        o anterior em vez de virar uma duplicata.
      </CabecalhoDaPagina>
      <div className={`conteudo ${estilos.grade}`}>
        <FormularioDeRelato />
        <aside className={estilos.lateral} aria-label="O que acontece com o relato">
          <Aparecer>
            <h2 className={estilos.tituloDaLateral}>O que acontece com o seu relato</h2>
            <ol className={estilos.caminho}>
              {CAMINHO_DO_RELATO.map(({ icone, titulo, texto }) => (
                <li key={titulo}>
                  <span className={estilos.icone}>
                    <Icone nome={icone} tamanho={20} />
                  </span>
                  <div>
                    <h3>{titulo}</h3>
                    <p>{texto}</p>
                  </div>
                </li>
              ))}
            </ol>
          </Aparecer>
          <Aparecer atraso={120} className={estilos.emergencia}>
            <h2>
              <Icone nome="telefone" tamanho={20} />
              Risco imediato?
            </h2>
            <p>
              Este formulário não aciona equipes. Em deslizamento, alagamento ou risco de
              desabamento, ligue para a Defesa Civil do Recife: <strong>0800 081 3400</strong>. Para
              pedir um serviço com protocolo, use a <strong>Central 156</strong>.
            </p>
          </Aparecer>
        </aside>
      </div>
    </>
  )
}
