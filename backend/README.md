# Backend

API REST do RecifeView. Ela autentica o gestor, aplica as permissões, registra a auditoria dos acessos e vai devolver os indicadores já calculados (agregações, percentis, per capita, reincidência e priorização) para o frontend.

**Stack:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic e PostgreSQL 17. As versões ficam no `uv.lock`; o porquê de cada ferramenta está em [docs/stack.md](../docs/stack.md#backend) e na [ADR 0004](../docs/adr/0004-ferramentas-complementares.md).

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) 0.13 ou superior. Ele instala o Python 3.12 sozinho, a partir do `.python-version`.
- PostgreSQL 17, de um destes jeitos:
  - **Com Docker:** na raiz do repositório, `docker compose up -d banco`.
  - **Sem Docker:** uma instalação local do PostgreSQL 17 com o usuário `recifeview` (senha `recifeview_local`) e os bancos `recifeview` e `recifeview_teste`.

## Como rodar

Na pasta `backend/`:

```bash
uv sync                       # cria o .venv e instala as dependências
cp .env.example .env          # depois troque API_SEGREDO_JWT por um segredo novo
uv run alembic upgrade head   # cria as tabelas no schema app
uv run uvicorn app.main:criar_aplicacao --factory --reload --port 8000
```

A API fica em http://localhost:8000/api/v1 e a documentação interativa (OpenAPI) em http://localhost:8000/api/v1/docs.

Para gerar o segredo do `.env`:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Com Docker, o banco de testes precisa ser criado uma vez:

```bash
docker compose exec banco createdb -U recifeview recifeview_teste
```

## Contas de acesso

Não existe cadastro aberto. A administração cria as contas pela linha de comando, e cada conta nasce com uma senha temporária que precisa ser trocada no primeiro acesso.

```bash
uv run recifeview cadastrar-usuario --email nome@recife.pe.gov.br --nome "Nome Completo"
uv run recifeview cadastrar-usuario --email outra@recife.pe.gov.br --nome "Outra Pessoa" --perfil ADMINISTRADOR
uv run recifeview redefinir-senha --email nome@recife.pe.gov.br
```

A senha temporária aparece uma única vez no terminal. Entregue por um canal seguro. `redefinir-senha` também desbloqueia a conta e derruba as sessões abertas.

Para apresentações, o grupo combina uma conta de demonstração local, descrita no [README da raiz](../README.md#conta-de-demonstração). Ela segue o mesmo fluxo: é criada por este comando e recebe a senha combinada no primeiro acesso.

## Variáveis de ambiente

Todas ficam no `.env` (que não vai para o git). O modelo é o [.env.example](.env.example).

| Variável | Para quê | Exemplo |
|---|---|---|
| `API_URL_DO_BANCO` | Conexão com o PostgreSQL | `postgresql+psycopg://recifeview:recifeview_local@localhost:5432/recifeview` |
| `API_SEGREDO_JWT` | Assina os tokens de acesso. No mínimo 32 caracteres | gerado com o comando acima |
| `API_MINUTOS_DO_TOKEN_DE_ACESSO` | Validade do token de acesso | `15` |
| `API_HORAS_DA_SESSAO` | Validade da sessão (cookie) | `12` |
| `API_COOKIE_SEGURO` | `true` exige HTTPS para o cookie de sessão. Localmente, `false` | `false` |
| `API_ORIGENS_PERMITIDAS` | Origens que podem chamar a API direto, em JSON | `[]` |
| `API_URL_DO_BANCO_DE_TESTE` | Banco dos testes de integração. Sem ela, esses testes são pulados | `postgresql+psycopg://...@localhost:5432/recifeview_teste` |

## Comandos

| Comando | O que faz |
|---|---|
| `uv run uvicorn app.main:criar_aplicacao --factory --reload --port 8000` | Sobe a API com recarga automática |
| `uv run alembic upgrade head` | Aplica as migrações |
| `uv run alembic revision -m "descricao"` | Cria uma migração nova em `migrations/versions/` |
| `uv run pytest` | Roda os testes (unidade, API e integração) |
| `uv run ruff format .` | Formata o código |
| `uv run ruff check .` | Lint |
| `uv run mypy app tests` | Checagem de tipos (modo estrito) |
| `uv run lint-imports` | Confere a regra da dependência entre as camadas |
| `uv run recifeview --help` | Administração de contas |

## Rotas

Todas sob `/api/v1`. Os erros seguem o formato `{"erro": {"codigo", "mensagem", "detalhes"}}`, descrito em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#api-rest).

| Método e caminho | O que faz |
|---|---|
| `GET /saude` | Confirma que a API está no ar |
| `POST /autenticacao/entrar` | Recebe e-mail e senha; devolve o token de acesso e grava o cookie de sessão |
| `POST /autenticacao/renovar` | Emite um token de acesso novo a partir do cookie de sessão |
| `POST /autenticacao/sair` | Encerra a sessão e apaga o cookie |
| `GET /autenticacao/eu` | Devolve o usuário do token de acesso |
| `POST /autenticacao/trocar-senha` | Troca a senha, derruba as outras sessões e abre uma nova |

As rotas de dados (indicadores, território, prazos, recorrências, fluxo da Câmara, catálogos e modelos) entram uma por tela, como previsto em [docs/arquitetura.md](../docs/arquitetura.md#telas-e-rotas-da-api).

Como a autenticação funciona, e por que ela ainda é uma proposta, está na [ADR 0005](../docs/adr/0005-autenticacao-com-jwt-proprio.md).

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `api`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#backend-fastapi). O router valida e chama um caso de uso; o caso de uso aplica as regras do domínio e usa portas; os repositórios SQLAlchemy implementam as portas. O `lint-imports` impede que uma camada interna importe uma externa.

```
app/
  domain/           usuario, sessao, email, senha, acesso, erros
  application/      portas/, casos_de_uso/, sessoes.py
  infrastructure/   db/, repositories/, auth/ (Argon2 e JWT), settings.py, relogio.py
  api/              routers/, schemas/, dependencias.py, erros.py, cookies.py
  main.py           monta a aplicação
  cli.py            administração de contas
migrations/         Alembic
tests/              unidade/, api/, integracao/
```

## Regra de privacidade

Nenhuma rota devolve o texto da SEDEC nem o hash da senha. Os schemas de resposta são explícitos justamente para que uma coluna nova no banco não vaze por acidente. A auditoria guarda o tipo do evento, o usuário e o horário, sem IP e sem o e-mail digitado. Ver [docs/dados.md](../docs/dados.md#privacidade-lgpd).

## Banco de dados

As migrações ficam nesta pasta, para que o esquema tenha um dono só. As tabelas de acesso ficam no schema `app`: `usuario`, `sessao` e `evento_de_acesso`. Convenções de nomes em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#banco-de-dados-postgresql).
