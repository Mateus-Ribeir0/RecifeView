import { ID_DO_CONTEUDO_PRINCIPAL, PularParaConteudo } from '../../components/PularParaConteudo'
import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { CabecalhoPublico } from './CabecalhoPublico'
import { ChamadaDeAcesso } from './ChamadaDeAcesso'
import { FaixaDeNumeros } from './FaixaDeNumeros'
import { RodapePublico } from './RodapePublico'
import { SecaoAbertura } from './SecaoAbertura'
import { SecaoAchados } from './SecaoAchados'
import { SecaoFontes } from './SecaoFontes'
import { SecaoPainel } from './SecaoPainel'
import { SecaoProblema } from './SecaoProblema'
import { SecaoProjeto } from './SecaoProjeto'

export function PaginaInicial() {
  useTituloDaPagina(null)

  return (
    <>
      <PularParaConteudo />
      <CabecalhoPublico />
      <main id={ID_DO_CONTEUDO_PRINCIPAL} tabIndex={-1}>
        <SecaoAbertura />
        <FaixaDeNumeros />
        <SecaoProblema />
        <SecaoAchados />
        <SecaoPainel />
        <SecaoFontes />
        <SecaoProjeto />
        <ChamadaDeAcesso />
      </main>
      <RodapePublico />
    </>
  )
}
