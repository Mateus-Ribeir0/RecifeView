# 0008. Levar a navegação e os filtros do painel para a barra lateral

- **Status:** proposta
- **Data:** 05/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação foi pedida por Mateus Ribeiro

## Contexto

O [design-system.md](../design-system.md) previa navegação no cabeçalho e uma barra de filtros fixa no topo. O protótipo em Streamlit, que o grupo apresentou na N4, usa barra lateral com a narrativa em grupos e os filtros logo abaixo. O painel agora tem duas áreas de naturezas diferentes: ler os dados e trazer dados novos.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Barra lateral com duas partes: Painel e Importações | Mesma dinâmica já validada na N4; oito telas cabem em grupos com nome; filtros sempre à vista | Tira cerca de 280px da largura. Por isso ela recolhe |
| Cabeçalho e filtros no topo, como previa o design system | Mais largura para gráficos | Oito telas não cabem bem numa linha; a barra de filtros toma altura em toda tela |

## Decisão

Usar a barra lateral em `azul-claro`, com uma chave de duas partes no topo. Em Painel ficam os grupos de telas e os filtros globais; em Importações ficam a nova importação e o histórico.

Também ficam registradas as escolhas de código da primeira tela de dados:

- **Cache de consultas:** o TanStack Query segue como proposta, então o painel usa um hook próprio e pequeno, `useConsulta`, em `application/consultas`. Trocar depois mexe nos hooks, não nas telas.
- **Mapa:** o react-leaflet segue como proposta, então o `MapaCoropletico` usa o Leaflet direto, em `ui/map`.

## Consequências

- O [design-system.md](../design-system.md#layout-do-painel) passa a descrever a barra lateral.
- A War Room mantém as nove placas do protótipo, acima do limite de quatro KPIs: é uma tela de operações, feita para bater o olho em tela cheia.
- Em telas menores que 1040px, a barra vira uma gaveta aberta por um botão.
