import estilos from './Importacoes.module.css'

const ETAPAS = ['Enviar', 'Colunas', 'Decisões', 'Revisar', 'Carga']

export function EtapasDaImportacao({ atual }: { atual: number }) {
  return (
    <ol className={estilos.etapas} aria-label="Etapas da importação">
      {ETAPAS.map((etapa, indice) => {
        const numero = indice + 1
        const classe =
          numero === atual ? estilos.etapaAtual : numero < atual ? estilos.etapaFeita : ''
        return (
          <li key={etapa} className={classe} aria-current={numero === atual ? 'step' : undefined}>
            <span aria-hidden="true">{numero}</span>
            {etapa}
          </li>
        )
      })}
    </ol>
  )
}
