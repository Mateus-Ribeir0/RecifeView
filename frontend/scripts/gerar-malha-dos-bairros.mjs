import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const URL_DO_PORTAL =
  'https://dados.recife.pe.gov.br/dataset/1702c764-ec7a-4ef0-9861-8acd0e40c819/resource/5c67ce14-1799-40c4-a37c-9daa04d1761c/download/bairros-do-recife.geojson'
const TOLERANCIA_EM_GRAUS = 0.00012
const CASAS_DECIMAIS = 5
const PONTOS_MINIMOS_DO_ANEL = 4
const DESTINO = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../src/ui/map/dados/bairros-recife.json',
)

async function lerMalhaOriginal(caminhoLocal) {
  if (caminhoLocal) return JSON.parse(await readFile(caminhoLocal, 'utf8'))
  const resposta = await fetch(URL_DO_PORTAL)
  if (!resposta.ok) throw new Error(`O portal respondeu ${resposta.status}`)
  return resposta.json()
}

function distanciaAoSegmento([x, y], [x1, y1], [x2, y2]) {
  const dx = x2 - x1
  const dy = y2 - y1
  const comprimento = dx * dx + dy * dy
  const t =
    comprimento === 0 ? 0 : Math.max(0, Math.min(1, ((x - x1) * dx + (y - y1) * dy) / comprimento))
  return Math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
}

function simplificarPorDouglasPeucker(pontos, tolerancia) {
  const manter = new Array(pontos.length).fill(false)
  manter[0] = true
  manter[pontos.length - 1] = true
  const pilha = [[0, pontos.length - 1]]
  while (pilha.length > 0) {
    const [inicio, fim] = pilha.pop()
    let maiorDistancia = 0
    let indiceMaisDistante = -1
    for (let indice = inicio + 1; indice < fim; indice += 1) {
      const distancia = distanciaAoSegmento(pontos[indice], pontos[inicio], pontos[fim])
      if (distancia > maiorDistancia) {
        maiorDistancia = distancia
        indiceMaisDistante = indice
      }
    }
    if (maiorDistancia > tolerancia) {
      manter[indiceMaisDistante] = true
      pilha.push([inicio, indiceMaisDistante], [indiceMaisDistante, fim])
    }
  }
  return pontos.filter((_, indice) => manter[indice])
}

function arredondar([longitude, latitude]) {
  return [Number(longitude.toFixed(CASAS_DECIMAIS)), Number(latitude.toFixed(CASAS_DECIMAIS))]
}

function simplificarAnel(anel) {
  const simplificado = simplificarPorDouglasPeucker(anel, TOLERANCIA_EM_GRAUS)
  return (simplificado.length >= PONTOS_MINIMOS_DO_ANEL ? simplificado : anel).map(arredondar)
}

function converterBairro({ properties, geometry }) {
  const poligonos = geometry.type === 'MultiPolygon' ? geometry.coordinates : [geometry.coordinates]
  return {
    type: 'Feature',
    properties: {
      codigo: properties.CBAIRRCODI,
      nome: properties.EBAIRRNOMEOF,
      rpa: properties.CRPAAACODI,
    },
    geometry: {
      type: 'MultiPolygon',
      coordinates: poligonos.map((poligono) => poligono.map(simplificarAnel)),
    },
  }
}

function contarPontos(malha) {
  return malha.features
    .flatMap((bairro) => bairro.geometry.coordinates.flat())
    .reduce((total, anel) => total + anel.length, 0)
}

const original = await lerMalhaOriginal(process.argv[2])
const malha = {
  type: 'FeatureCollection',
  fonte:
    'Prefeitura do Recife, Portal de Dados Abertos, conjunto Área urbana, recurso Bairros do Recife',
  licenca: 'ODbL',
  features: original.features
    .map(converterBairro)
    .sort((a, b) => a.properties.nome.localeCompare(b.properties.nome, 'pt-BR')),
}
await mkdir(dirname(DESTINO), { recursive: true })
const conteudo = JSON.stringify(malha)
await writeFile(DESTINO, `${conteudo}\n`)
console.log(
  `${malha.features.length} bairros, ${contarPontos(malha)} pontos, ` +
    `${Math.round(Buffer.byteLength(conteudo) / 1024)} KB em ${DESTINO}`,
)
