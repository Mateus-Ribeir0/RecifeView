import estilos from './RodapeDoPainel.module.css'

export function RodapeDoPainel() {
  return (
    <footer className={estilos.rodape}>
      <p>
        Dados abertos da Prefeitura do Recife (ODbL), Câmara Municipal e IBGE. Projetos 5, CESAR
        School, 2026.2, Grupo 08. Construído com auxílio de IA (Claude, Anthropic); o grupo revisou
        o conteúdo.
      </p>
    </footer>
  )
}
