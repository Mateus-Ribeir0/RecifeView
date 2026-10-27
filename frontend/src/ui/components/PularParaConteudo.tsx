import estilos from './PularParaConteudo.module.css'

export const ID_DO_CONTEUDO_PRINCIPAL = 'conteudo-principal'

export function PularParaConteudo() {
  return (
    <a href={`#${ID_DO_CONTEUDO_PRINCIPAL}`} className={estilos.link}>
      Pular para o conteúdo
    </a>
  )
}
