# Frontend

SPA do painel do RecifeView, usada por gestores públicos para ver, por bairro, serviço e período, onde as demandas se repetem, demoram ou ficam sem resposta.

**Stack:** React, Recharts e Leaflet. As ferramentas complementares estão em [docs/stack.md](../docs/stack.md#frontend).

> Ainda não há código nesta pasta. Ao criar o projeto, preencha as seções marcadas com "a preencher" no mesmo commit.

## Telas

| Tela | O que mostra | Rota da API |
|---|---|---|
| Login | Autenticação do gestor | Autenticação |
| Visão Geral | KPIs-síntese e alertas | Indicadores |
| Mapa por Bairro/RPA | Demanda per capita, reincidência e os dois mapas de prioridade | Território |
| Prazos | Mediana e p90 por serviço e órgão | Prazos |
| Recorrências | Duplicidade e reincidência por local | Recorrências |
| Fluxo Câmara → Prefeitura | Funil e Sankey de envio e resposta | Fluxo Câmara → Prefeitura |

Detalhes em [docs/arquitetura.md](../docs/arquitetura.md#spa).

## Pré-requisitos

A preencher: versão do Node.js (`.nvmrc`) e gerenciador de pacotes.

## Como rodar

A preencher:

1. Instalar as dependências.
2. Copiar `.env.example` para `.env` e ajustar.
3. Subir o servidor de desenvolvimento (indicar porta e URL).

## Variáveis de ambiente

| Variável | Para quê | Exemplo |
|---|---|---|
| A preencher | | |

## Comandos

| Comando | O que faz |
|---|---|
| A preencher | Desenvolvimento, build, lint, formatação, testes |

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `ui`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#frontend-react). Em resumo: página não chama `fetch`, componente recebe tipos do domínio, Recharts só em `ui/charts` e Leaflet só em `ui/map`.

## Visual

Toda tela segue [docs/design-system.md](../docs/design-system.md). Cores, fontes e espaçamentos vêm dos tokens em `src/ui/theme/`, nunca de valores soltos.
