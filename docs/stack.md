# Stack

O que cada parte do sistema usa, por quê e com que grau de certeza.

| Status | Significado |
|---|---|
| **Definido** | Decidido pelo grupo. Use. |
| **Do C3** | Está no diagrama C3 v0.1. Use, a menos que o grupo mude o diagrama. |
| **Proposta** | Recomendação ainda não confirmada. Antes de instalar, confirme com o grupo e registre uma ADR. |

Quando uma proposta for confirmada, troque o status aqui e crie a ADR correspondente.

## Definido pelo grupo (26/10/2026)

| Camada | Tecnologia | Papel |
|---|---|---|
| Frontend | React | SPA do painel |
| Frontend | Recharts | Gráficos (séries, barras, dispersão, funil, Sankey) |
| Frontend | Leaflet | Mapa coroplético dos 94 bairros |
| Backend | Python + FastAPI | API REST |
| Banco | PostgreSQL | Camadas tratada e analítica, usuários, auditoria |
| Processor | Python | Ingestão e transformação dos dados da Prefeitura |
| Processor | AWS EventBridge | Regra agendada (cron ou rate) que dispara o Processor |

Registro: [ADR 0001](adr/0001-stack-do-projeto.md) e [ADR 0002](adr/0002-leaflet-para-mapa-coropletico.md).

## Frontend

| Ferramenta | Status | Por quê |
|---|---|---|
| React Router | Do C3 | Shell da aplicação e proteção de rotas |
| TypeScript | Proposta | Tipar os contratos da API evita uma classe inteira de erro entre frontend e backend |
| Vite | Proposta | Servidor de desenvolvimento e build. O Create React App foi descontinuado |
| react-leaflet | Proposta | Integra o Leaflet ao ciclo de vida do React sem manipular o DOM na mão |
| TanStack Query | Proposta | É o "cache de consultas" do C3: cache, revalidação e estados de carregamento e erro |
| ESLint + Prettier | Proposta | Lint e formatação padronizados |
| Vitest + Testing Library | Proposta | Testes de componentes e de funções de formatação |
| eslint-plugin-boundaries | Proposta | Barra importação que fere a regra da dependência (ex.: Recharts fora de `ui/charts`, `fetch` fora de `infrastructure/api`) |

Fonte tipográfica: Montserrat (ver [design-system.md](design-system.md#tipografia)).

## Backend

| Ferramenta | Status | Por quê |
|---|---|---|
| Pydantic v2 | Definido (vem com o FastAPI) | Validação de entrada e esquemas de resposta |
| SQLAlchemy 2 | Do C3 | Repositórios e consultas parametrizadas |
| Alembic | Proposta | Migrações versionadas do esquema |
| psycopg 3 | Proposta | Driver do PostgreSQL |
| Uvicorn | Proposta | Servidor ASGI |
| pytest | Proposta | Testes |

## Processor

| Ferramenta | Status | Por quê |
|---|---|---|
| pandas | Definido (pipeline atual) | O `pipeline.py` e o `build_dataset.py` do Drive já usam, e as contagens deles já foram conferidas |
| Onde roda: Lambda ou ECS/Fargate | Em aberto | O Lambda tem limite de 15 minutos, e a carga histórica tem cerca de 2,6 milhões de linhas. Ver [decisões em aberto](adr/README.md#decisões-em-aberto) |
| AWS Secrets Manager | Proposta (está no C3 como "a decidir") | Guardar o sal do `id_local` |

## Python (backend e processor)

| Ferramenta | Status | Por quê |
|---|---|---|
| Python 3.12 ou superior | Proposta | Mesma linha do Colab, onde o notebook da EDA roda |
| uv + `pyproject.toml` | Proposta | Ambiente virtual, dependências e lockfile numa ferramenta só, rápida e reproduzível |
| Ruff | Proposta | Lint e formatação |
| mypy | Proposta | Checagem de tipos |
| import-linter | Proposta | Barra importação que fere a regra da dependência (ex.: `domain` importando SQLAlchemy) |

## Infraestrutura e repositório

| Ferramenta | Status | Por quê |
|---|---|---|
| Docker Compose | Proposta | Subir o PostgreSQL local com um comando, todo mundo na mesma versão |
| Camada bruta: S3 ou schema `raw` | Em aberto | Ver [decisões em aberto](adr/README.md#decisões-em-aberto) |
| Autenticação: JWT próprio ou serviço gerenciado (ex.: Cognito) | Em aberto | Ver [decisões em aberto](adr/README.md#decisões-em-aberto) |
| GitHub Actions | Proposta | CI com lint e testes em cada PR, quando houver repositório remoto |
| pre-commit + commitlint | Proposta | Barrar formatação errada e mensagem de commit fora do padrão antes do commit |

## Versões

- Fixe versões assim que a ferramenta entrar no projeto: `package-lock.json` no frontend, `uv.lock` no Python, imagem com tag exata no Docker Compose.
- Node.js: use a LTS ativa na data de criação do frontend e registre a versão em `.nvmrc`.
- Python: registre a versão em `.python-version`.
- PostgreSQL: a mesma versão principal no Docker Compose local e no ambiente de nuvem.
- Ao instalar ou atualizar qualquer coisa, atualize esta tabela e o README da pasta. A skill `atualizar-docs` tem o passo a passo.
