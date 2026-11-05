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
