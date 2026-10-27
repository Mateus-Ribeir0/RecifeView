# Frontend

SPA do RecifeView: a página inicial pública e o painel usado por gestores públicos para ver, por bairro, serviço e período, onde as demandas se repetem, demoram ou ficam sem resposta.

**Stack:** React 19, React Router, TypeScript e Vite, com Recharts e Leaflet previstos para as telas de dados. As versões ficam no `package-lock.json`; o porquê de cada ferramenta está em [docs/stack.md](../docs/stack.md#frontend) e na [ADR 0004](../docs/adr/0004-ferramentas-complementares.md).

## Pré-requisitos

- Node.js 22 LTS (a versão está no `.nvmrc`).
- A API rodando em http://localhost:8000 (ver [backend/README.md](../backend/README.md)). Sem ela, a página inicial abre, mas o login não funciona.

## Como rodar

Na pasta `frontend/`:

```bash
npm install
npm run dev
```

O painel fica em http://localhost:5173. Em desenvolvimento, o Vite repassa tudo que começa com `/api` para a API em `localhost:8000`, então navegador, cookie de sessão e API ficam na mesma origem.

## Telas

| Caminho          | Tela                                                                              | Acesso             |
| ---------------- | --------------------------------------------------------------------------------- | ------------------ |
| `/`              | Página inicial: o problema, os primeiros achados, o painel, as fontes e o projeto | Público            |
| `/entrar`        | Entrada com e-mail e senha                                                        | Só quem não entrou |
| `/entrar/ajuda`  | Senha esquecida, conta bloqueada, pedido de acesso                                | Público            |
| `/definir-senha` | Troca da senha temporária (obrigatória no primeiro acesso) ou troca voluntária    | Gestor             |
| `/painel`        | Visão geral, por enquanto com o andamento das telas de dados                      | Gestor             |

As próximas telas (Mapa por bairro e RPA, Prazos, Recorrências, Fluxo Câmara → Prefeitura) estão em [docs/arquitetura.md](../docs/arquitetura.md#telas-e-rotas-da-api).

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
| `npm run preview`   | Serve a versão de produção localmente                           |
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
  domain/           usuario, senha, erros, acesso, territorio, formatacao
  application/      autenticacao/ (porta do serviço, provedor e hook da sessão)
  infrastructure/   api/ (cliente HTTP e serviço de autenticação)
  ui/
    app/            rotas, guardas de rota e montagem (único lugar que conhece a infraestrutura)
    pages/          inicio/, entrar/, ajuda-de-acesso/, definir-senha/, painel/, nao-encontrada/
    components/     logo, botões, campos, avisos, layout das telas de acesso
    map/            mapa SVG dos bairros e a malha
    conteudo/       textos compartilhados entre páginas
    theme/          tokens do design system e estilos base
  main.tsx          ponto de entrada
```

## Visual

Toda tela segue [docs/design-system.md](../docs/design-system.md). Cores, fontes e espaçamentos vêm dos tokens em `src/ui/theme/tokens.css`, nunca de valores soltos.
