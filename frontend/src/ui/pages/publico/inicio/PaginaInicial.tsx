import { useTituloDaPagina } from '../../../components/useTituloDaPagina'
import { Abertura } from './Abertura'
import { ChamadaFinal } from './ChamadaFinal'
import { ComOuSemConta } from './ComOuSemConta'
import { FaixaDeNumeros } from './FaixaDeNumeros'
import { RazoesParaRelatar } from './RazoesParaRelatar'
import { SecaoDoMapa } from './SecaoDoMapa'

export function PaginaInicial() {
  useTituloDaPagina(null)

  return (
    <>
      <Abertura />
      <FaixaDeNumeros />
      <RazoesParaRelatar />
      <ComOuSemConta />
      <SecaoDoMapa />
      <ChamadaFinal />
    </>
  )
}
