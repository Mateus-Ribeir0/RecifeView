import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { Abertura } from './Abertura'
import { CaminhoDaDemanda } from './CaminhoDaDemanda'
import { ChamadaFinal } from './ChamadaFinal'
import { FaixaDeNumeros } from './FaixaDeNumeros'
import { ResumoDoQueMuda } from './ResumoDoQueMuda'
import { SecaoDoMapa } from './SecaoDoMapa'

export function PaginaInicial() {
  useTituloDaPagina(null)

  return (
    <>
      <Abertura />
      <FaixaDeNumeros />
      <ResumoDoQueMuda />
      <CaminhoDaDemanda />
      <SecaoDoMapa />
      <ChamadaFinal />
    </>
  )
}
