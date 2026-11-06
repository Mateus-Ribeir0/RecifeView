import type { ReactNode } from 'react'

const DESENHOS = {
  menu: <path d="M3 6h18M3 12h18M3 18h18" />,
  fechar: <path d="M6 6l12 12M18 6L6 18" />,
  abrir: <path d="M6 9l6 6 6-6" />,
  seta: <path d="M5 12h14M13 6l6 6-6 6" />,
  inicio: (
    <>
      <rect x="3" y="3" width="8" height="10" rx="1" />
      <rect x="13" y="3" width="8" height="6" rx="1" />
      <rect x="13" y="11" width="8" height="10" rx="1" />
      <rect x="3" y="15" width="8" height="6" rx="1" />
    </>
  ),
  pulso: <path d="M3 12h4l3-8 4 16 3-8h4" />,
  retorno: <path d="M9 15l-5-5 5-5M4 10h11a5 5 0 0 1 0 10h-3" />,
  repetir: <path d="M17 2l4 4-4 4M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4M21 13v2a3 3 0 0 1-3 3H3" />,
  relogio: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  local: (
    <>
      <path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z" />
      <circle cx="12" cy="10" r="2.5" />
    </>
  ),
  bandeira: <path d="M5 21V4M5 4h13l-3 4 3 4H5" />,
  importar: <path d="M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />,
  informacao: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5M12 8h.01" />
    </>
  ),
  filtro: <path d="M3 5h18l-7 8v6l-4 2v-8z" />,
  reproduzir: <path d="M7 5l12 7-12 7z" />,
  sortear: <path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5" />,
  voltar: <path d="M3 12a9 9 0 1 0 3-6.7M3 4v5h5" />,
  alerta: <path d="M12 3l10 18H2zM12 10v5M12 18h.01" />,
  baixar: <path d="M12 4v12M7 11l5 5 5-5M4 20h16" />,
  relato: <path d="M4 5h16v11H9l-5 4zM8 9h8M8 12h5" />,
  confirmado: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12.5l2.8 2.8L16 9.5" />
    </>
  ),
  escudo: <path d="M12 3l7 3v5c0 5-3 8.5-7 10-4-1.5-7-5-7-10V6zM9 12l2 2 4-4" />,
  base: (
    <>
      <ellipse cx="12" cy="6" rx="7.5" ry="3" />
      <path d="M4.5 6v12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V6M4.5 12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3" />
    </>
  ),
  somar: <path d="M6 4v6a6 6 0 0 0 6 6h6M18 4v6M14 12l4 4-4 4" />,
  telas: <path d="M4 5h16v12H4zM9 21h6M12 17v4M8 13V9M12 13V8M16 13v-2" />,
  lampada: (
    <path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.100h5c0-.9.4-1.6 1-2.100A6 6 0 0 0 12 3z" />
  ),
  limpeza: <path d="M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5" />,
  arvore: (
    <path d="M12 21v-7M12 14l-3-3M12 11l3-3M12 3a6 6 0 0 0-5.5 8.4A4 4 0 0 0 9 18h6a4 4 0 0 0 2.5-6.6A6 6 0 0 0 12 3z" />
  ),
  gota: <path d="M12 3s7 7.2 7 12a7 7 0 0 1-14 0c0-4.8 7-12 7-12z" />,
  via: <path d="M8 3L4 21M16 3l4 18M12 4v3M12 11v3M12 18v3" />,
  telefone: (
    <path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a3 3 0 0 1-3 3A15 15 0 0 1 3 6a3 3 0 0 1 3-3z" />
  ),
  pessoas: (
    <>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M16 5.2a3.5 3.5 0 0 1 0 5.6M18 14.5c1.9.8 3 2.8 3 5.5" />
    </>
  ),
} as const satisfies Readonly<Record<string, ReactNode>>

export type NomeDoIcone = keyof typeof DESENHOS

interface Propriedades {
  nome: NomeDoIcone
  tamanho?: number
}

export function Icone({ nome, tamanho = 20 }: Propriedades) {
  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {DESENHOS[nome]}
    </svg>
  )
}
