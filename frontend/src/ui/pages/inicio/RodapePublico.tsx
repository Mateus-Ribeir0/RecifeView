import { Logo } from '../../components/Logo'
import { LINKS_DO_PROJETO } from './conteudo'
import estilos from './RodapePublico.module.css'

export function RodapePublico() {
  return (
    <footer className={estilos.rodape}>
      <div className={`conteudo ${estilos.grade}`}>
        <div className={estilos.marca}>
          <Logo variante="branco" altura={28} />
          <p>Painel analítico das demandas do cidadão no Recife, para a gestão pública.</p>
        </div>
        <div>
          <h2 className={estilos.titulo}>Dados</h2>
          <p>
            Portal de Dados Abertos do Recife (licença ODbL), Câmara Municipal do Recife (SAGL) e
            IBGE (Censo 2022).
          </p>
        </div>
        <div>
          <h2 className={estilos.titulo}>Aviso</h2>
          <p>Projeto acadêmico, sem vínculo oficial com a Prefeitura do Recife.</p>
        </div>
      </div>
      <div className={`conteudo ${estilos.base}`}>
        <p>Grupo 08 · Projetos 5 · CESAR School · 2026.2</p>
        <a href={LINKS_DO_PROJETO.codigo}>Código aberto no GitHub</a>
      </div>
    </footer>
  )
}
