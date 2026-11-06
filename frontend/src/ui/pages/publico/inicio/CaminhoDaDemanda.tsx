import { Aparecer } from '../../../components/Aparecer'
import { prefereMenosMovimento } from '../../../components/movimento'
import secao from '../Secao.module.css'
import estilos from './CaminhoDaDemanda.module.css'

interface Entrada {
  nome: string
  cor: string
}

const ENTRADAS: readonly Entrada[] = [
  { nome: 'Central 156 / Emlurb', cor: 'var(--cor-fonte-156)' },
  { nome: 'Defesa Civil', cor: 'var(--cor-fonte-defesa-civil)' },
  { nome: 'Ouvidoria', cor: 'var(--cor-fonte-ouvidoria)' },
  { nome: 'SEDEC', cor: 'var(--cor-fonte-sedec)' },
  { nome: 'Câmara Municipal', cor: 'var(--cor-fonte-camara)' },
  { nome: 'Formulário público', cor: 'var(--cor-fonte-formulario)' },
]

const ETAPAS = [
  { titulo: 'Pente fino', detalhe: 'compara e pergunta', x: 430 },
  { titulo: 'Base única', detalhe: 'bairro, serviço, período', x: 660 },
  { titulo: 'Painel da gestão', detalhe: 'onde agir primeiro', x: 890 },
] as const

const LARGURA_DA_ENTRADA = 220
const ALTURA_DA_ENTRADA = 44
const DISTANCIA_ENTRE_ENTRADAS = 62
const LARGURA_DA_ETAPA = 190
const ALTURA_DA_ETAPA = 96
const CENTRO_VERTICAL = 178
const DURACAO_DO_PERCURSO_EM_S = 5

function caminhoDaEntrada(indice: number): string {
  const y = indice * DISTANCIA_ENTRE_ENTRADAS + ALTURA_DA_ENTRADA / 2
  const destino = ETAPAS[0].x
  return `M${LARGURA_DA_ENTRADA} ${y} C 320 ${y}, 330 ${CENTRO_VERTICAL}, ${destino} ${CENTRO_VERTICAL}`
}

function caminhoCompleto(indice: number): string {
  const fim = ETAPAS[2].x
  return `${caminhoDaEntrada(indice)} L ${fim} ${CENTRO_VERTICAL}`
}

function Pontos() {
  if (prefereMenosMovimento()) return null
  return ENTRADAS.map(({ nome, cor }, indice) => (
    <circle key={nome} r={6} fill={cor} stroke="var(--cor-branco)" strokeWidth={2}>
      <animateMotion
        dur={`${DURACAO_DO_PERCURSO_EM_S}s`}
        begin={`${indice * 0.8}s`}
        repeatCount="indefinite"
        path={caminhoCompleto(indice)}
      />
    </circle>
  ))
}

function Diagrama() {
  return (
    <svg
      viewBox="0 0 1090 356"
      role="img"
      aria-label="As cinco fontes e o formulário público passam pelo pente fino, chegam à base única e seguem para o painel da gestão"
      className={estilos.diagrama}
    >
      {ENTRADAS.map(({ nome }, indice) => (
        <path key={nome} d={caminhoDaEntrada(indice)} className={estilos.ligacao} />
      ))}
      <path
        d={`M${ETAPAS[0].x} ${CENTRO_VERTICAL} L${ETAPAS[2].x} ${CENTRO_VERTICAL}`}
        className={estilos.ligacao}
      />
      <Pontos />
      {ENTRADAS.map(({ nome, cor }, indice) => {
        const y = indice * DISTANCIA_ENTRE_ENTRADAS
        return (
          <g key={nome}>
            <rect
              y={y}
              width={LARGURA_DA_ENTRADA}
              height={ALTURA_DA_ENTRADA}
              rx={4}
              className={estilos.entrada}
            />
            <circle cx={22} cy={y + ALTURA_DA_ENTRADA / 2} r={6} fill={cor} />
            <text x={40} y={y + ALTURA_DA_ENTRADA / 2 + 5} className={estilos.nomeDaEntrada}>
              {nome}
            </text>
          </g>
        )
      })}
      {ETAPAS.map(({ titulo, detalhe, x }) => (
        <g key={titulo}>
          <rect
            x={x}
            y={CENTRO_VERTICAL - ALTURA_DA_ETAPA / 2}
            width={LARGURA_DA_ETAPA}
            height={ALTURA_DA_ETAPA}
            rx={8}
            className={estilos.etapa}
          />
          <text
            x={x + LARGURA_DA_ETAPA / 2}
            y={CENTRO_VERTICAL - 4}
            textAnchor="middle"
            className={estilos.tituloDaEtapa}
          >
            {titulo}
          </text>
          <text
            x={x + LARGURA_DA_ETAPA / 2}
            y={CENTRO_VERTICAL + 20}
            textAnchor="middle"
            className={estilos.detalheDaEtapa}
          >
            {detalhe}
          </text>
        </g>
      ))}
    </svg>
  )
}

export function CaminhoDaDemanda() {
  return (
    <section className={secao.secao} aria-labelledby="titulo-caminho">
      <div className="conteudo">
        <Aparecer>
          <p className={secao.rotulo}>Como funciona</p>
          <h2 id="titulo-caminho" className={secao.titulo}>
            Seis entradas, uma conferência, um painel
          </h2>
          <p className={secao.abertura}>
            Arquivos das fontes e relatos do formulário passam pelo mesmo pente fino. O que for
            repetido é somado ou vai para a decisão de uma pessoa, e só depois chega aos
            indicadores.
          </p>
        </Aparecer>
        <Aparecer className={estilos.moldura}>
          <Diagrama />
          <ol className={estilos.listaNoCelular}>
            <li>As cinco fontes e o formulário público entram no sistema.</li>
            {ETAPAS.map(({ titulo, detalhe }) => (
              <li key={titulo}>
                <strong>{titulo}:</strong> {detalhe}.
              </li>
            ))}
          </ol>
        </Aparecer>
      </div>
    </section>
  )
}
