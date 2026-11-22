import { useEffect, useId, useRef, useState } from 'react'
import { Link } from 'react-router'

import { useNotificacoes } from '../../application/notificacoes/useNotificacoes'
import { formatarNumero } from '../../domain/formatacao'
import { descreverQuando, type Notificacao } from '../../domain/notificacoes'
import { Icone } from './Icone'
import estilos from './Sino.module.css'

const MAXIMO_NO_CONTADOR = 99

function rotuloDoBotao(naoLidas: number): string {
  if (naoLidas === 0) return 'Notificações, nenhuma nova'
  return `Notificações, ${formatarNumero(naoLidas)} ${naoLidas === 1 ? 'nova' : 'novas'}`
}

interface ItemProps {
  item: Notificacao
  aoAbrir: (item: Notificacao) => void
}

function ItemDaCaixa({ item, aoAbrir }: ItemProps) {
  return (
    <li>
      <Link
        to={item.caminho}
        className={`${estilos.item} ${item.lida ? '' : estilos.naoLida}`}
        onClick={() => aoAbrir(item)}
      >
        <span className={estilos.titulo}>
          {!item.lida && <span className="visualmente-oculto">Nova: </span>}
          {item.titulo}
        </span>
        <span className={estilos.texto}>{item.texto}</span>
        <time className={estilos.quando} dateTime={item.criadaEm}>
          {descreverQuando(item.criadaEm, new Date())}
        </time>
      </Link>
    </li>
  )
}

/** Avisos do ciclo dentro da plataforma: o mesmo que vai por e-mail, sempre à mão. */
export function Sino() {
  const { caixa, indisponivel, marcarComoLida, marcarTodasComoLidas } = useNotificacoes()
  const [aberto, definirAberto] = useState(false)
  const idDoPainel = useId()
  const raiz = useRef<HTMLDivElement>(null)
  const gatilho = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!aberto) return
    function fecharComEsc(evento: KeyboardEvent) {
      if (evento.key !== 'Escape') return
      definirAberto(false)
      gatilho.current?.focus()
    }
    function fecharAoClicarFora(evento: PointerEvent) {
      if (!raiz.current?.contains(evento.target as Node)) definirAberto(false)
    }
    document.addEventListener('keydown', fecharComEsc)
    document.addEventListener('pointerdown', fecharAoClicarFora)
    return () => {
      document.removeEventListener('keydown', fecharComEsc)
      document.removeEventListener('pointerdown', fecharAoClicarFora)
    }
  }, [aberto])

  function abrir(item: Notificacao) {
    definirAberto(false)
    if (!item.lida) void marcarComoLida(item.id)
  }

  return (
    <div className={estilos.raiz} ref={raiz}>
      <button
        ref={gatilho}
        type="button"
        className={estilos.gatilho}
        aria-expanded={aberto}
        aria-controls={idDoPainel}
        aria-label={rotuloDoBotao(caixa.naoLidas)}
        onClick={() => definirAberto((atual) => !atual)}
      >
        <Icone nome="sino" tamanho={22} />
        {caixa.naoLidas > 0 && (
          <span className={`${estilos.contador} numero`} aria-hidden="true">
            {caixa.naoLidas > MAXIMO_NO_CONTADOR ? `${MAXIMO_NO_CONTADOR}+` : caixa.naoLidas}
          </span>
        )}
      </button>
      {aberto && (
        <section id={idDoPainel} className={estilos.painel} aria-label="Notificações">
          <header className={estilos.cabecalho}>
            <h2>Notificações</h2>
            {caixa.naoLidas > 0 && (
              <button
                type="button"
                className={estilos.marcarTodas}
                onClick={() => void marcarTodasComoLidas()}
              >
                Marcar todas como lidas
              </button>
            )}
          </header>
          {indisponivel && (
            <p className={estilos.aviso}>
              Não foi possível atualizar agora. A próxima tentativa é em 30 segundos.
            </p>
          )}
          {caixa.itens.length === 0 ? (
            <p className={estilos.vazio}>
              Nada por aqui ainda. Quando uma ocorrência que você acompanha mudar de etapa, o aviso
              aparece neste sino e também por e-mail, se estiver ligado.
            </p>
          ) : (
            <ul className={estilos.lista}>
              {caixa.itens.map((item) => (
                <ItemDaCaixa key={item.id} item={item} aoAbrir={abrir} />
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  )
}
