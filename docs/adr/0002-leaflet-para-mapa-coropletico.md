# 0002. Usar Leaflet para o mapa coroplético

- **Status:** aceita
- **Data:** 26/10/2026
- **Quem decidiu:** grupo

## Contexto

O mapa por bairro e RPA é a funcionalidade mais bem pontuada na matriz da Semana 5 (empatada com a análise de prazos), e a N3 pede dois mapas de prioridade. O Recharts, escolhido para os gráficos, não desenha mapas. O C4 v0.1 deixou em aberto a escolha entre Leaflet e MapLibre.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Leaflet | Simples, maduro, bem documentado, leve; GeoJSON de 94 polígonos é trivial para ele; integração pronta com React (react-leaflet) | Renderização em SVG/Canvas, não em WebGL; fica mais lento com dezenas de milhares de pontos |
| MapLibre GL | WebGL, aguenta muitos pontos, estilos vetoriais | Mais complexo de configurar e de estilizar; exagero para 94 polígonos |

## Decisão

Leaflet, com o GeoJSON dos 94 bairros oficiais e cores definidas pelo [design system](../design-system.md#mapas-leaflet).

## Consequências

- O mapa principal é coroplético por bairro. Pontos, se entrarem, ficam numa camada secundária agregada, porque as coordenadas do 156 têm cobertura baixa e não aleatória.
- Se um dia for preciso mostrar centenas de milhares de pontos, reavaliar com uma nova ADR.
- O mapa de fundo exige atribuição (OpenStreetMap e o provedor escolhido).
