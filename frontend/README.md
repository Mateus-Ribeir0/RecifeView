# Frontend

SPA do RecifeView: a página inicial pública e o painel usado por gestores públicos para ver, por bairro, serviço e período, onde as demandas se repetem, demoram ou ficam sem resposta.

**Stack:** React 19, React Router, TypeScript e Vite, com Recharts nos gráficos e Leaflet no mapa. As versões ficam no `package-lock.json`; o porquê de cada ferramenta está em [docs/stack.md](../docs/stack.md#frontend) e na [ADR 0004](../docs/adr/0004-ferramentas-complementares.md).

## Pré-requisitos

- Node.js 22 LTS (a versão está no `.nvmrc`).
- A API rodando em http://localhost:8000, com a base carregada (ver [backend/README.md](../backend/README.md#carregar-os-dados)). Sem a API, o site público abre, mas o login e o formulário não funcionam. Sem a base, as telas do painel abrem vazias.

## Como rodar

Na pasta `frontend/`:

```bash
npm install
npm run dev
```

O painel fica em http://localhost:5173. Em desenvolvimento, o Vite repassa tudo que começa com `/api` para a API em `localhost:8000`, então navegador, cookie de sessão e API ficam na mesma origem.

Para conferir a versão de produção, gere o build e sirva a pasta `dist/`, com a API rodando:

```bash
npm run build
npm run preview
```

Ela fica em http://localhost:4173, com o mesmo repasse de `/api`.

## Telas

| Caminho                  | Tela                                                                              | Acesso             |
| ------------------------ | --------------------------------------------------------------------------------- | ------------------ |
| `/`                      | Início: abertura, números, o que muda, caminho da demanda e mapa                  | Público            |
| `/o-que-muda`            | Os problemas de antes, o que muda e a evidência de cada um                        | Público            |
| `/plataforma`            | As telas do painel, com capturas reais                                            | Público            |
| `/dados-e-confianca`     | Pente fino, fontes, privacidade e leitura honesta dos números                     | Público            |
| `/contribuir`            | Formulário público em três passos                                                 | Público            |
| `/entrar`                | Entrada com e-mail e senha                                                        | Só quem não entrou |
| `/entrar/ajuda`          | Senha esquecida, conta bloqueada, pedido de acesso                                | Público            |
| `/definir-senha`         | Troca da senha temporária (obrigatória no primeiro acesso) ou troca voluntária    | Gestor             |
| `/painel`                | Início: principais indicadores e volume por fonte                                 | Gestor             |
| `/painel/war-room`       | Estado de um dia: o que está parado e por onde começar                            | Gestor             |
| `/painel/retorno`        | Abas da Câmara e da Ouvidoria: para onde vai cada pedido e quanto volta           | Gestor             |
| `/painel/reincidencia`   | Local repetido, intervalos e pontos crônicos                                      | Gestor             |
| `/painel/prazos`         | Percentis, faixas, categorias e estoque aberto                                    | Gestor             |
| `/painel/territorio`     | Mapa, tabela e tendência por bairro                                               | Gestor             |
| `/painel/prioridade`     | Abas: índice AHP com mapa e ranking, ocorrências, método e sensibilidade          | Gestor             |
| `/painel/sobre-os-dados` | Cobertura, glossário e correções aplicadas                                        | Gestor             |
| `/painel/contribuicoes`  | Pente fino dos relatos, ocorrências e geração do pacote                           | Gestor             |
| `/painel/importacoes`    | Histórico; `/nova` envia um arquivo e `/:id` mostra os passos e o relatório       | Gestor             |

A correspondência entre telas e rotas da API está em [docs/arquitetura.md](../docs/arquitetura.md#telas-e-rotas-da-api).

## Variáveis de ambiente

Nenhuma é obrigatória em desenvolvimento. O modelo é o [.env.example](.env.example).

| Variável          | Para quê             | Padrão    |
| ----------------- | -------------------- | --------- |
| `VITE_URL_DA_API` | Endereço base da API | `/api/v1` |

## Comandos

| Comando             | O que faz                                                       |
| ------------------- | --------------------------------------------------------------- |
| `npm run dev`       | Servidor de desenvolvimento com recarga                         |
| `npm run build`     | Checa os tipos e gera a versão de produção em `dist/`           |
| `npm run preview`   | Serve a versão de produção em http://localhost:4173             |
| `npm test`          | Roda os testes (Vitest e Testing Library)                       |
| `npm run lint`      | ESLint, incluindo a regra de camadas e a proibição de travessão |
| `npm run typecheck` | Checagem de tipos                                               |
| `npm run format`    | Formata com Prettier                                            |
| `npm run malha`     | Regenera a malha simplificada dos bairros (ver abaixo)          |

## Malha dos bairros

O mapa usa `src/ui/map/dados/bairros-recife.json`: os 94 bairros oficiais com nome e RPA, simplificados de cerca de 47 mil para 3,4 mil pontos (tolerância de uns 13 m). O arquivo é gerado por `scripts/gerar-malha-dos-bairros.mjs` a partir do recurso "Bairros do Recife" do Portal de Dados Abertos (licença ODbL). Para usar uma cópia local em vez de baixar do portal: `npm run malha -- caminho/para/bairros.geojson`.

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `ui`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#frontend-react). O ESLint (eslint-plugin-boundaries) barra importação fora da regra: o domínio não importa React nem biblioteca externa, a interface não importa a infraestrutura, Recharts só entra em `ui/charts` e Leaflet só em `ui/map`.

```
src/
  domain/           usuario, senha, erros, acesso, territorio, formatacao, painel, filtros, importacoes, contribuicoes
  application/      autenticacao/, filtros/, consultas/ (cache e hooks do painel), importacoes/, contribuicoes/
  infrastructure/   api/ (cliente HTTP, conversão e serviços que implementam as portas)
  ui/
    app/            rotas, guardas de rota e montagem (único lugar que conhece a infraestrutura)
    pages/          publico/ (as abas do site), entrar/, ajuda-de-acesso/, definir-senha/, painel/, importacoes/, contribuicoes/, nao-encontrada/
    components/     logo, botões, campos, avisos, KPIs, cartões, abas, ícones, tabela, estados da consulta
    charts/         gráficos: os do Recharts (únicos que o importam) e funil, sparkline e composição em HTML e SVG
    map/            mapa SVG dos bairros, minimapa das RPAs, mapa coroplético (Leaflet) e a malha
    conteudo/       textos compartilhados entre páginas
    assets/         marca, foto do Recife e capturas reais do painel
    theme/          tokens do design system e estilos base
  main.tsx          ponto de entrada
```

## Visual

Toda tela segue [docs/design-system.md](../docs/design-system.md). Cores, fontes e espaçamentos vêm dos tokens em `src/ui/theme/tokens.css`, nunca de valores soltos.
