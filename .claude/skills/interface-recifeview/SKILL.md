---
name: interface-recifeview
description: Aplica a identidade visual e as regras de visualização do RecifeView em qualquer coisa que o usuário vê: telas React, componentes, gráficos Recharts, mapas Leaflet, textos de interface, capturas para entrega e peças de pitch. Use antes de criar ou alterar qualquer elemento visual ou texto de tela, e ao revisar se algo "parece genérico" ou "tem cara de IA".
---

# Interface do RecifeView

A referência completa é [docs/design-system.md](../../../docs/design-system.md). Leia esse documento antes da primeira mudança visual da sessão. Abaixo estão o resumo e a checagem final.

## Referência rápida

**Cores oficiais:** `#0F62FE` azul principal · `#EAF2FF` azul claro · `#000000` texto · `#FFFFFF` fundo.
**Derivadas:** `#062A5F` azul-marinho (do logo) · `#0043CE` azul escuro (hover e foco).
**Neutros:** `#525252` texto secundário · `#6F6F6F` eixos e notas · `#C6C6C6` contexto e sem dado · `#E0E0E0` bordas e grade · `#F4F4F4` fundo alternativo.
**Escala do mapa (5 classes):** `#EAF2FF` `#A6C8FF` `#4589FF` `#0F62FE` `#062A5F`.
**Cor por fonte:** 156 `#0F62FE` · Ouvidoria `#005D5D` · Câmara `#B28600` · Defesa Civil `#9F1853` · SEDEC `#8A3800`.
**Tipografia:** Montserrat 400, 500, 600 e 700. Números com `tabular-nums`.
**Forma:** espaçamento em múltiplos de 4px, raio de 4px (campos) e 8px (cartões), borda de 1px em vez de sombra.

As cores vêm sempre dos tokens em `frontend/src/ui/theme/`. Recharts só é importado em `ui/charts` e Leaflet só em `ui/map` (ver [docs/clean-architecture.md](../../../docs/clean-architecture.md#frontend-react)). Se o token não existir, crie-o no tema e documente-o no design system. Nunca escreva hexadecimal direto no componente.

## Ao fazer uma tela

1. Comece pela pergunta que a tela responde e escreva essa pergunta como subtítulo.
2. No máximo 4 KPIs no topo. Cada um com rótulo, valor, período e fonte.
3. A barra de filtros globais fica no lugar de sempre e mostra o resumo do que está aplicado.
4. Toda área de dado tem os estados carregando, vazio e erro.
5. Abaixo de cada gráfico, a nota com fonte, período, filtros e n.

## Ao fazer um gráfico

- O título afirma ou pergunta algo sobre o dado.
- A série em foco fica em azul principal e as demais em `#C6C6C6`.
- Rótulo direto em vez de legenda, quando couber.
- Grade só horizontal e eixo de barras começando em zero.
- Para prazos, mostre mediana e p90, nunca só a média.
- Nada de pizza com mais de 3 fatias, rosca, 3D, gauge ou eixo duplo.

## Ao fazer um mapa

- Coroplético por `bairro_oficial`, com taxa por mil habitantes e bairros de menos de 1.000 moradores filtrados.
- 5 classes por quantis, com os limites na legenda. "Sem dado" em cinza hachurado.
- Uma tabela ordenada ao lado, com os mesmos valores.
- Mantenha a atribuição do mapa de fundo.

## Texto de interface

- Português claro, para gestor público: "pedidos", "demandas", "bairro", "órgão".
- Números `1.377.158`, `36,3%`; datas `dd/mm/aaaa`; períodos `2021 a 2025`.
- Nenhum travessão (—) nem meia-risca (–). Use vírgula, dois-pontos, parênteses ou ponto: "RPA 3 (Norte)", "Prazos por serviço".
- Diga o que o número não é ("sem resposta registrada" não quer dizer "não atendido").
- Nada de "Bem-vindo(a)!", "Insights", "Descubra", "Poderoso" ou exclamações.

## Checagem final: tem cara de gerado por IA?

Antes de dar como pronto, responda. Qualquer "sim" precisa ser corrigido.

- [ ] Tem emoji em algum lugar?
- [ ] Tem travessão ou meia-risca em algum texto?
- [ ] Tem gradiente, brilho, glassmorphism ou fundo escuro "tech"?
- [ ] Tem ícone decorativo em título ou cartão que não representa uma ação?
- [ ] Tem frase genérica que serviria a qualquer cidade ou a qualquer painel?
- [ ] Tem número fictício sem a marcação "dado fictício"?
- [ ] Tem cor fora dos tokens?
- [ ] Algum gráfico está sem fonte, período ou n?
- [ ] Algum texto informa só pela cor?
- [ ] Os cantos estão muito arredondados ou há sombras grandes?

## Verificação visual

Quando houver frontend rodando, abra a tela no navegador e confira em 1280px e em 768px. Para entregas, anexe a captura de tela ao PR.
