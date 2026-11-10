import { useTituloDaPagina } from '../../components/useTituloDaPagina'
import { FormularioDeRelato } from '../publico/contribuir/FormularioDeRelato'
import estilos from './Cidade.module.css'

export function PaginaRelatarNaCidade() {
  useTituloDaPagina('Relatar um problema')

  return (
    <>
      <h1 className={estilos.titulo}>Relatar um problema</h1>
      <p className={estilos.subtitulo}>
        Leva um minuto. Se alguém já relatou o mesmo problema, o seu relato reforça o anterior.
      </p>
      <div className={estilos.formularioRelatar}>
        <FormularioDeRelato />
        <aside className={estilos.observacao}>
          <h2>Só você sabe que o relato é seu</h2>
          <p>
            Ele fica em Meus relatos, para você acompanhar a revisão. A gestão revisa sem saber quem
            enviou, e em Relatos da cidade ele aparece sem o número exato e sem o que você escreveu.
          </p>
          <p>
            Em risco imediato, ligue para a Defesa Civil do Recife: <strong>0800 081 3400</strong>.
          </p>
        </aside>
      </div>
    </>
  )
}
