import { Aparecer } from '../../../components/Aparecer'
import { Icone, type NomeDoIcone } from '../../../components/Icone'
import { LinkDeBotao } from '../../../components/LinkDeBotao'
import estilos from './ChamadaFinal.module.css'

interface Caminho {
  icone: NomeDoIcone
  titulo: string
  texto: string
  para: string
  acao: string
}

const CAMINHOS: readonly Caminho[] = [
  {
    icone: 'telas',
    titulo: 'Para quem está na gestão',
    texto:
      'Entre com o e-mail e a senha recebidos da administração. No primeiro acesso, você define a sua senha.',
    para: '/entrar',
    acao: 'Entrar no painel',
  },
  {
    icone: 'relato',
    titulo: 'Para quem mora no Recife',
    texto:
      'Conte o que está acontecendo na sua rua, sem se identificar. O relato ajuda a gestão a enxergar o que os arquivos não mostram.',
    para: '/contribuir',
    acao: 'Relatar um problema',
  },
]

export function ChamadaFinal() {
  return (
    <section className={estilos.chamada} aria-label="Por onde continuar">
      <div className={`conteudo ${estilos.grade}`}>
        {CAMINHOS.map(({ icone, titulo, texto, para, acao }, indice) => (
          <Aparecer key={para} atraso={indice * 120}>
            <span className={estilos.icone}>
              <Icone nome={icone} tamanho={28} />
            </span>
            <h2 className={estilos.titulo}>{titulo}</h2>
            <p className={estilos.texto}>{texto}</p>
            <LinkDeBotao para={para} variante="claro">
              {acao}
            </LinkDeBotao>
          </Aparecer>
        ))}
      </div>
    </section>
  )
}
