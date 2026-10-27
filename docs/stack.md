# Stack

O que cada parte do sistema usa, por quê e com que grau de certeza.

| Status | Significado |
|---|---|
| **Definido** | Decidido pelo grupo. Use. |
| **Do C3** | Está no diagrama C3 v0.1. Use, a menos que o grupo mude o diagrama. |
| **Proposta** | Recomendação ainda não confirmada. Antes de instalar, confirme com o grupo e registre uma ADR. |
| **Em aberto** | Decisão pendente, listada em [adr/README.md](adr/README.md#decisões-em-aberto). |

Quando uma proposta for confirmada, troque o status aqui e crie a ADR correspondente. As versões exatas ficam nos lockfiles (`frontend/package-lock.json` e `backend/uv.lock`); a coluna "Versão" registra a linha principal em uso.

## Base (ADR 0001 e 0002)

| Camada | Tecnologia | Status | Papel |
|---|---|---|---|
| Frontend | React 19 | Definido | SPA do painel e página inicial |
| Frontend | Recharts | Definido | Gráficos (séries, barras, dispersão, funil, Sankey). Entra com a primeira tela de dados |
| Frontend | Leaflet | Definido | Mapa coroplético dos 94 bairros. Entra com a tela do mapa |
| Backend | Python 3.12 + FastAPI | Definido | API REST |
| Banco | PostgreSQL 17 | Definido | Camadas tratada e analítica, usuários, auditoria |
| Processor | Python | Definido | Ingestão e transformação dos dados da Prefeitura |
| Processor | AWS EventBridge | Definido | Regra agendada (cron ou rate) que dispara o Processor |

## Frontend

| Ferramenta | Versão | Status | Por quê |
|---|---|---|---|
| TypeScript | 6 | Definido ([ADR 0004](adr/0004-ferramentas-complementares.md)) | Contratos da API checados em tempo de compilação |
| Vite | 8 | Definido | Servidor de desenvolvimento, proxy para a API e build |
| React Router | 8 | Definido (Do C3) | Rotas, guardas de rota e restauração da rolagem |
| ESLint + typescript-eslint | 10 / 8 | Definido | Lint, com regra própria contra travessão |
| eslint-plugin-boundaries | 7 | Definido | Barra importação que fere a regra da dependência |
| Prettier | 3 | Definido | Formatação |
| Vitest + Testing Library + jsdom | 5 / 16 / 30 | Definido | Testes de domínio, cliente HTTP, sessão e telas |
| TanStack Query | | Proposta | É o "cache de consultas" do C3. Confirmar com o grupo quando entrar a primeira tela de dados |
| react-leaflet | | Proposta | Integração do Leaflet com o React |

Fonte tipográfica: Montserrat, pelo Google Fonts (ver [design-system.md](design-system.md#tipografia)).

## Backend

| Ferramenta | Versão | Status | Por quê |
|---|---|---|---|
| Pydantic + pydantic-settings | 2 | Definido | Validação de entrada, schemas de resposta e configuração por variável de ambiente |
| SQLAlchemy | 2 | Definido (Do C3) | Repositórios e consultas parametrizadas |
| Alembic | 1 | Definido | Migrações versionadas do esquema |
| psycopg | 3 | Definido | Driver do PostgreSQL |
| Uvicorn | 0.54 | Definido | Servidor ASGI |
| argon2-cffi | 25 | Definido ([ADR 0005](adr/0005-autenticacao-com-jwt-proprio.md)) | Hash das senhas |
| PyJWT | 2 | Definido ([ADR 0005](adr/0005-autenticacao-com-jwt-proprio.md)) | Token de acesso |
| pytest + httpx2 | 9 / 2 | Definido | Testes de unidade, de API (TestClient) e de integração |

## Processor

| Ferramenta | Status | Por quê |
|---|---|---|
| pandas | Definido (pipeline atual) | O `pipeline.py` e o `build_dataset.py` do Drive já usam, e as contagens deles já foram conferidas |
| Onde roda: Lambda ou ECS/Fargate | Em aberto | O Lambda tem limite de 15 minutos, e a carga histórica tem cerca de 2,6 milhões de linhas |
| AWS Secrets Manager | Proposta (está no C3 como "a decidir") | Guardar o sal do `id_local` |

## Python (backend e processor)

| Ferramenta | Versão | Status | Por quê |
|---|---|---|---|
| uv + `pyproject.toml` | 0.13 | Definido | Ambiente virtual, Python, dependências e lockfile numa ferramenta só |
| Ruff | 0.17 | Definido | Lint e formatação |
| mypy | 2 | Definido | Checagem de tipos em modo estrito |
| import-linter | 2 | Definido | Barra importação que fere a regra da dependência |

## Infraestrutura e repositório

| Ferramenta | Status | Por quê |
|---|---|---|
| Docker Compose | Definido | Subir o PostgreSQL local com um comando, todo mundo na mesma versão (`docker-compose.yml` na raiz) |
| Camada bruta: S3 ou schema `raw` | Em aberto | Ver [decisões em aberto](adr/README.md#decisões-em-aberto) |
| Autenticação: JWT próprio ou serviço gerenciado | Em aberto, com proposta | A [ADR 0005](adr/0005-autenticacao-com-jwt-proprio.md) descreve o JWT próprio já implementado atrás de uma porta |
| GitHub Actions | Proposta | CI com os mesmos comandos de lint, tipos e testes dos READMEs |
| pre-commit + commitlint | Proposta | Barrar formatação errada e mensagem de commit fora do padrão antes do commit |

## Versões

- Node.js 22 LTS, registrada em `frontend/.nvmrc`. O React Router 8 exige pelo menos a 22.22.
- Python 3.12, registrada em `backend/.python-version`. O uv instala sozinho.
- PostgreSQL 17, a mesma versão principal no Docker Compose (`postgres:17.10`) e no ambiente de nuvem.
- Ao instalar ou atualizar qualquer coisa, atualize esta tabela e o README da pasta. A skill `atualizar-docs` tem o passo a passo.
