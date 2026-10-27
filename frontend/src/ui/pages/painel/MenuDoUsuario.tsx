import { useEffect, useId, useRef, useState } from 'react'
import { Link } from 'react-router'

import { iniciaisDoNome, rotuloDoPerfil, type Usuario } from '../../../domain/usuario'
import estilos from './MenuDoUsuario.module.css'

interface Propriedades {
  usuario: Usuario
  aoSair: () => void
}

export function MenuDoUsuario({ usuario, aoSair }: Propriedades) {
  const [aberto, definirAberto] = useState(false)
  const idDoMenu = useId()
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

  return (
    <div className={estilos.raiz} ref={raiz}>
      <button
        ref={gatilho}
        type="button"
        className={estilos.gatilho}
        aria-expanded={aberto}
        aria-controls={idDoMenu}
        aria-label={`Menu da conta de ${usuario.nome}`}
        onClick={() => definirAberto((atual) => !atual)}
      >
        <span className={estilos.iniciais} aria-hidden="true">
          {iniciaisDoNome(usuario.nome)}
        </span>
        <span className={estilos.identificacao}>
          <span className={estilos.nome}>{usuario.nome}</span>
          <span className={estilos.perfil}>{rotuloDoPerfil(usuario.perfil)}</span>
        </span>
      </button>
      {aberto && (
        <div id={idDoMenu} className={estilos.menu}>
          <p className={estilos.email}>{usuario.email}</p>
          <ul>
            <li>
              <Link to="/definir-senha" className={estilos.item}>
                Trocar senha
              </Link>
            </li>
            <li>
              <button type="button" className={estilos.item} onClick={aoSair}>
                Sair
              </button>
            </li>
          </ul>
        </div>
      )}
    </div>
  )
}
