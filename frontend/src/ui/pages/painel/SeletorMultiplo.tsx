import { useEffect, useId, useMemo, useRef, useState } from 'react'

import estilos from './SeletorMultiplo.module.css'

export interface OpcaoDoSeletor {
  valor: string
  rotulo: string
}

interface Propriedades {
  rotulo: string
  placeholder: string
  opcoes: readonly OpcaoDoSeletor[]
  selecionados: readonly string[]
  aoMudar: (selecionados: string[]) => void
}

const OPCOES_PARA_BUSCA = 8

function semAcento(texto: string): string {
  return texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

export function SeletorMultiplo({
  rotulo,
  placeholder,
  opcoes,
  selecionados,
  aoMudar,
}: Propriedades) {
  const [aberto, definirAberto] = useState(false)
  const [busca, definirBusca] = useState('')
  const raiz = useRef<HTMLDivElement>(null)
  const idDaLista = useId()
  const visiveis = useMemo(() => {
    const termo = semAcento(busca)
    return opcoes.filter((opcao) => semAcento(opcao.rotulo).includes(termo))
  }, [opcoes, busca])
  const nomes = new Map(opcoes.map((opcao) => [opcao.valor, opcao.rotulo]))

  useEffect(() => {
    if (!aberto) return
    function fecharAoClicarFora(evento: PointerEvent) {
      if (!raiz.current?.contains(evento.target as Node)) definirAberto(false)
    }
    function fecharComEsc(evento: KeyboardEvent) {
      if (evento.key === 'Escape') definirAberto(false)
    }
    document.addEventListener('pointerdown', fecharAoClicarFora)
    document.addEventListener('keydown', fecharComEsc)
    return () => {
      document.removeEventListener('pointerdown', fecharAoClicarFora)
      document.removeEventListener('keydown', fecharComEsc)
    }
  }, [aberto])

  function alternar(valor: string) {
    aoMudar(
      selecionados.includes(valor)
        ? selecionados.filter((item) => item !== valor)
        : [...selecionados, valor],
    )
  }

  return (
    <div className={estilos.seletor} ref={raiz}>
      <span className={estilos.rotulo}>{rotulo}</span>
      <button
        type="button"
        className={estilos.gatilho}
        aria-expanded={aberto}
        aria-controls={idDaLista}
        aria-label={`${rotulo}: ${selecionados.length ? `${selecionados.length} escolhidos` : placeholder}`}
        onClick={() => definirAberto((atual) => !atual)}
      >
        {selecionados.length === 0 ? placeholder : `${selecionados.length} escolhido(s)`}
        <span aria-hidden="true">▾</span>
      </button>
      {selecionados.length > 0 && (
        <ul className={estilos.escolhidos}>
          {selecionados.map((valor) => (
            <li key={valor}>
              <button
                type="button"
                className={estilos.etiqueta}
                aria-label={`Tirar ${nomes.get(valor) ?? valor}`}
                onClick={() => alternar(valor)}
              >
                {nomes.get(valor) ?? valor}
                <span aria-hidden="true"> ×</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {aberto && (
        <div id={idDaLista} className={estilos.lista}>
          {opcoes.length > OPCOES_PARA_BUSCA && (
            <input
              type="search"
              className={estilos.busca}
              placeholder="Buscar"
              aria-label={`Buscar em ${rotulo}`}
              value={busca}
              onChange={(evento) => definirBusca(evento.target.value)}
            />
          )}
          <ul>
            {visiveis.map((opcao) => (
              <li key={opcao.valor}>
                <label className={estilos.opcao}>
                  <input
                    type="checkbox"
                    checked={selecionados.includes(opcao.valor)}
                    onChange={() => alternar(opcao.valor)}
                  />
                  {opcao.rotulo}
                </label>
              </li>
            ))}
            {visiveis.length === 0 && <li className={estilos.semOpcao}>Nada encontrado</li>}
          </ul>
        </div>
      )}
    </div>
  )
}
