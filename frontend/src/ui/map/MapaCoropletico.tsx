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

const OPACIDADE_COM_SELECAO = 0.65
const OPACIDADE_FORA_DO_RECORTE = 0.2
const PESO_NO_HOVER = 2
const PESO_DA_SELECAO = 2

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

function preenchimento(
  valor: ValorDoBairro | undefined,
  escala: readonly (string | undefined)[],
  idDaHachura: string,
): string | undefined {
  const classe = valor?.classe
  return classe === null || classe === undefined ? `url(#${idDaHachura})` : escala[classe - 1]
}

function opacidade(valor: ValorDoBairro | undefined, haSelecao: boolean): number {
  if (valor?.emDestaque === false) return OPACIDADE_FORA_DO_RECORTE
  return haSelecao ? OPACIDADE_COM_SELECAO : 1
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
  const pintarAtual = useRef<(item: Layer) => void>(() => undefined)
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
      zoomControl: false,
      scrollWheelZoom: false,
      zoomSnap: 0.25,
      preferCanvas: false,
    })
    L.control.zoom({ position: 'topright' }).addTo(novoMapa)
    const novaCamada = L.geoJSON(malha as unknown as GeoJSON.GeoJsonObject, {
      onEachFeature: (_, item) => {
        item.on('click', () => aoClicarAtual.current?.(nomeDaFeicao(item)))
        item.on('mouseover', () => {
          const caminho = item as L.Path
          caminho.setStyle({ color: lerToken('--cor-azul-marinho'), weight: PESO_NO_HOVER })
          caminho.bringToFront()
        })
        item.on('mouseout', () => pintarAtual.current(item))
      },
    }).addTo(novoMapa)
    const enquadrar = () => {
      novoMapa.invalidateSize()
      novoMapa.fitBounds(novaCamada.getBounds(), { padding: [8, 8] })
    }
    enquadrar()
    const observador = new ResizeObserver(enquadrar)
    observador.observe(elemento.current)
    criarHachura(novoMapa, idDaHachura)
    mapa.current = novoMapa
    camada.current = novaCamada
    return () => {
      observador.disconnect()
      novoMapa.remove()
      mapa.current = null
      camada.current = null
    }
  }, [malha, idDaHachura])

  useEffect(() => {
    const escala = TOKENS_DA_ESCALA.map(lerToken)
    const branco = lerToken('--cor-branco')
    const preto = lerToken('--cor-preto')
    const corDaSelecao = lerToken('--cor-selecao')
    const haSelecao = Boolean(selecionado)

    function pintar(item: Layer) {
      const nome = nomeDaFeicao(item)
      const valor = valores.get(nome)
      const emFoco = selecionado === nome
      ;(item as L.Path).setStyle({
        fillColor: emFoco ? corDaSelecao : preenchimento(valor, escala, idDaHachura),
        fillOpacity: emFoco ? 1 : opacidade(valor, haSelecao),
        color: emFoco ? preto : branco,
        weight: emFoco ? PESO_DA_SELECAO : 1,
      })
    }

    pintarAtual.current = pintar
    camada.current?.eachLayer((item) => {
      pintar(item)
      const nome = nomeDaFeicao(item)
      const caminho = item as L.Path
      const emFoco = selecionado === nome
      if (emFoco) caminho.bringToFront()
      caminho.unbindTooltip()
      caminho.bindTooltip(emFoco ? nome : (valores.get(nome)?.dica ?? nome), {
        permanent: emFoco,
        sticky: !emFoco,
        direction: emFoco ? 'top' : 'auto',
        className: emFoco ? estilos.rotuloFixo : estilos.dica,
      })
    })
  }, [valores, selecionado, malha, idDaHachura])

  return (
    <div>
      <div
        ref={elemento}
        className={`${estilos.mapa} ${aoClicar ? '' : estilos.semClique}`}
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
