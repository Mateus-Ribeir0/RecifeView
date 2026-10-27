import { LinkDeBotao } from '../../components/LinkDeBotao'
import { Logo } from '../../components/Logo'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import estilos from './PaginaNaoEncontrada.module.css'

export function PaginaNaoEncontrada() {
  useTituloDaPagina('Página não encontrada')

  return (
    <main className={estilos.pagina}>
      <Logo altura={32} />
      <h1 className={estilos.titulo}>Página não encontrada</h1>
      <p className={estilos.texto}>
        O endereço pode ter mudado ou estar incompleto. Confira o link ou volte para a página
        inicial.
      </p>
      <LinkDeBotao para="/">Ir para a página inicial</LinkDeBotao>
    </main>
  )
}
