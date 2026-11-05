import 'leaflet/dist/leaflet.css'

import L, { type GeoJSON as CamadaGeoJson, type Layer, type Map as MapaLeaflet } from 'leaflet'
import { useEffect, useId, useRef, useState } from 'react'

import { carregarMalha, type FeicaoDeBairro, type MalhaDosBairros } from './carregarBairros'
import estilos from './MapaCoropletico.module.css'

export interface ValorDoBairro {
  classe: number | null
  emDestaque: boolean
  dica: string
}

interface Propriedades {
  rotulo: string
  valores: ReadonlyMap<string, ValorDoBairro>
  selecionado?: string | null
  aoClicar?: (nome: string) => void
  altura?: number
}

const TOKENS_DA_ESCALA = [
  '--cor-mapa-1',
  '--cor-mapa-2',
  '--cor-mapa-3',
  '--cor-mapa-4',
  '--cor-mapa-5',
]

function lerToken(token: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(token).trim()
}

function criarHachura(mapa: MapaLeaflet, id: string): void {
  const svg = mapa.getPanes().overlayPane.querySelector('svg')
  if (!svg || svg.querySelector(`#${CSS.escape(id)}`)) return
  const contexto = lerToken('--cor-contexto')
  const branco = lerToken('--cor-branco')
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
  defs.innerHTML = `<pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="${contexto}"/><line x1="0" y1="0" x2="0" y2="6" stroke="${branco}" stroke-width="2"/></pattern>`
  svg.prepend(defs)
}

function nomeDaFeicao(camada: Layer): string {
  const feicao = (camada as L.Polygon & { feature?: FeicaoDeBairro }).feature
  return feicao?.properties.nome ?? ''
}

export function MapaCoropletico({
  rotulo,
  valores,
  selecionado,
  aoClicar,
  altura = 460,
}: Propriedades) {
  const elemento = useRef<HTMLDivElement>(null)
  const mapa = useRef<MapaLeaflet | null>(null)
  const camada = useRef<CamadaGeoJson | null>(null)
  const aoClicarAtual = useRef(aoClicar)
  const [malha, definirMalha] = useState<MalhaDosBairros | null>(null)
  const idDaHachura = `hachura-${useId().replace(/[^a-zA-Z0-9]/g, '')}`

  useEffect(() => {
    aoClicarAtual.current = aoClicar
  }, [aoClicar])

  useEffect(() => {
    let ativo = true
    void carregarMalha().then((dados) => {
      if (ativo) definirMalha(dados)
    })
    return () => {
      ativo = false
    }
  }, [])

  useEffect(() => {
    if (!elemento.current || !malha) return
    const novoMapa = L.map(elemento.current, {
      attributionControl: false,
      scrollWheelZoom: false,
      zoomSnap: 0.25,
      preferCanvas: false,
    })
    const novaCamada = L.geoJSON(malha as unknown as GeoJSON.GeoJsonObject, {
      onEachFeature: (_, item) => {
        item.on('click', () => aoClicarAtual.current?.(nomeDaFeicao(item)))
      },
    }).addTo(novoMapa)
    novoMapa.fitBounds(novaCamada.getBounds(), { padding: [8, 8] })
    criarHachura(novoMapa, idDaHachura)
    mapa.current = novoMapa
    camada.current = novaCamada
    return () => {
      novoMapa.remove()
      mapa.current = null
      camada.current = null
    }
  }, [malha, idDaHachura])

  useEffect(() => {
    const escala = TOKENS_DA_ESCALA.map(lerToken)
    camada.current?.eachLayer((item) => {
      const nome = nomeDaFeicao(item)
      const valor = valores.get(nome)
      const emFoco = selecionado === nome
      const caminho = item as L.Path
      caminho.setStyle({
        fillColor:
          valor?.classe === null || valor?.classe === undefined
            ? `url(#${idDaHachura})`
            : escala[valor.classe - 1],
        fillOpacity: valor?.emDestaque === false ? 0.25 : 1,
        color: emFoco ? lerToken('--cor-preto') : lerToken('--cor-branco'),
        weight: emFoco ? 2 : 1,
      })
      if (emFoco) caminho.bringToFront()
      caminho.unbindTooltip()
      caminho.bindTooltip(valor?.dica ?? nome, { sticky: true, className: estilos.dica })
    })
  }, [valores, selecionado, malha, idDaHachura])

  return (
    <div>
      <div
        ref={elemento}
        className={estilos.mapa}
        style={{ height: altura }}
        role="img"
        aria-label={rotulo}
      />
      <p className={estilos.atribuicao}>
        Malha: Prefeitura do Recife, Portal de Dados Abertos (ODbL)
      </p>
    </div>
  )
}
