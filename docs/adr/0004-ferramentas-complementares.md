# 0004. Adotar as ferramentas complementares de frontend, backend e ambiente local

- **Status:** aceita
- **Data:** 26/10/2026
- **Quem decidiu:** grupo, confirmado por Mateus Ribeiro antes do primeiro código

## Contexto

A [ADR 0001](0001-stack-do-projeto.md) definiu React, FastAPI, PostgreSQL e o Processor agendado. Faltava escolher as ferramentas em volta de cada uma, listadas como "proposta" em [stack.md](../stack.md). O primeiro código (landing page e fluxo de login) precisa delas para existir.

## Opções consideradas

| Ponto | Escolha | Alternativa descartada | Por quê |
|---|---|---|---|
| Linguagem do frontend | TypeScript | JavaScript | Os contratos da API ficam checados em tempo de compilação |
| Build do frontend | Vite | Create React App | O CRA foi descontinuado; o Vite é o padrão atual do React |
| Rotas | React Router | Roteamento próprio | Já estava no C3 |
| Qualidade do frontend | ESLint (com eslint-plugin-boundaries), Prettier, Vitest e Testing Library | Só formatação | O plugin de fronteiras barra importação que fere a [Clean Architecture](0003-clean-architecture-e-clean-code.md) |
| Python | 3.12 com uv e `pyproject.toml` | pip e requirements | Ambiente, dependências e lockfile numa ferramenta só |
| Qualidade do Python | Ruff, mypy, pytest e import-linter | flake8 e black | O Ruff faz lint e formatação; o import-linter vigia as camadas |
| Banco no Python | SQLAlchemy 2, psycopg 3 e Alembic | SQL solto | Repositórios tipados e migrações versionadas |
| Servidor | Uvicorn | Gunicorn sozinho | Servidor ASGI de referência do FastAPI |
| PostgreSQL local | Docker Compose, ou instalação local para quem não tem Docker | Só Docker | Nem toda máquina do grupo roda Docker |

Ficam como proposta, para confirmar quando forem necessárias: o cache de consultas (TanStack Query), o react-leaflet, o GitHub Actions e o pre-commit com commitlint. O login não precisa de nenhuma delas.

## Decisão

Adotar as ferramentas da coluna "Escolha", com as versões fixadas nos lockfiles (`frontend/package-lock.json` e `backend/uv.lock`).

## Consequências

- [stack.md](../stack.md) passa essas ferramentas para "Definido".
- Node.js 22 LTS, Python 3.12 e PostgreSQL 17 são os pré-requisitos do README.
- O CI (GitHub Actions) pode rodar exatamente os mesmos comandos de lint, tipos e testes quando for configurado.
