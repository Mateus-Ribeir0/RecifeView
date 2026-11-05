# 0008. Navegação numa lateral recolhível e filtros numa linha acima do conteúdo

- **Status:** proposta
- **Data:** 05/11/2026 (revista no mesmo dia, depois da primeira versão com os filtros na lateral)
- **Quem decidiu:** a decidir pelo grupo; a implementação foi pedida por Mateus Ribeiro

## Contexto

O [design-system.md](../design-system.md) previa navegação no cabeçalho e uma barra de filtros fixa no topo. O protótipo em Streamlit, que o grupo apresentou na N4, usa barra lateral com a narrativa em grupos e os filtros logo abaixo.

A primeira versão seguiu o Streamlit, com uma chave Painel e Importações no topo e os filtros na lateral. Na revisão visual, isso se mostrou ruim: a lateral ficou longa, os filtros saíam da tela em notebooks, sumiam ao recolher a lateral, e cada tela precisava de avisos em texto sobre os filtros que não aplicava.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Lateral só com navegação, filtros numa linha acima do conteúdo | Filtros sempre à vista, inclusive com a lateral recolhida; cada tela mostra só os filtros que aplica; é o que o design system já pedia e a prática comum de visualização (uma linha de filtros acima dos gráficos) | Muda a dinâmica do Streamlit, que tinha os filtros na lateral |
| Lateral com navegação e filtros, como no Streamlit | Mesma dinâmica da N4 | Lateral longa, filtros somem ao recolher, telas cheias de avisos |
| Navegação e filtros no topo | Mais largura para gráficos | Nove telas não cabem bem numa linha |

## Decisão

- **Navegação:** barra lateral em `azul-claro`, com ícone e rótulo, que alterna entre aberta e recolhida (só ícones) por um botão de menu no cabeçalho, como no [UI shell do Carbon](https://www.carbondesignsystem.com/components/ui-shell-header/guidelines). A preferência fica salva no navegador. Abaixo de 1040px, ela vira gaveta sobre o conteúdo.
- **Menus:** quatro grupos: Visão geral, Onde o pedido se perde, Onde agir primeiro e Dados. Importações e Sobre os dados ficam juntos em Dados, no lugar da chave de duas partes. Nova importação é um botão dentro de Importações.
- **Filtros:** uma linha fixa acima do conteúdo. Cada tela declara quais filtros aplica em `telasDoPainel.ts`. War Room, Importações e Sobre os dados não têm a linha.
- **Telas longas:** Retorno, Prioridade e Sobre os dados se dividem em abas.

Também ficam registradas as escolhas de código da primeira tela de dados:

- **Cache de consultas:** o TanStack Query segue como proposta, então o painel usa um hook próprio e pequeno, `useConsulta`, em `application/consultas`. Trocar depois mexe nos hooks, não nas telas.
- **Mapa:** o react-leaflet segue como proposta, então o `MapaCoropletico` usa o Leaflet direto, em `ui/map`.
- **Ícones:** são desenhados em `ui/components/Icone.tsx`, sem dependência nova.

## Consequências

- O [design-system.md](../design-system.md#layout-do-painel) descreve a lateral, a linha de filtros e as abas.
- A War Room mostra cinco KPIs, um a mais que o limite, além da faixa do dia: é uma tela de operações, feita para bater o olho em tela cheia.
- Quem conhece o Streamlit encontra os mesmos filtros em outro lugar.
