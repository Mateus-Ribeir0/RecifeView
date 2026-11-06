import { useEffect, useState } from 'react'

import { formatarNumero } from '../../domain/formatacao'
import { prefereMenosMovimento } from './movimento'
import { useVisivelNaTela } from './useVisivelNaTela'

const DURACAO_EM_MS = 1400

function desacelerar(progresso: number): number {
  return 1 - (1 - progresso) ** 3
}

function useContagem(valor: number, ativa: boolean): number {
  const [atual, definirAtual] = useState(() => (prefereMenosMovimento() ? valor : 0))

  useEffect(() => {
    if (!ativa || prefereMenosMovimento()) return
    const inicio = performance.now()
    let quadro = requestAnimationFrame(function avancar(agora) {
      const progresso = Math.min((agora - inicio) / DURACAO_EM_MS, 1)
      definirAtual(Math.round(valor * desacelerar(progresso)))
      if (progresso < 1) quadro = requestAnimationFrame(avancar)
    })
    return () => cancelAnimationFrame(quadro)
  }, [valor, ativa])

  return atual
}

export function ContadorAnimado({ valor }: { valor: number }) {
  const [referencia, visivel] = useVisivelNaTela<HTMLSpanElement>()
  const atual = useContagem(valor, visivel)

  return (
    <span ref={referencia} className="numero">
      <span aria-hidden="true">{formatarNumero(atual)}</span>
      <span className="visualmente-oculto">{formatarNumero(valor)}</span>
    </span>
  )
}
