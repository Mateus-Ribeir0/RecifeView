# Backend

API REST do RecifeView. Ela autentica o gestor, registra a auditoria de acessos e consultas, devolve os indicadores já calculados (agregações, percentis, per capita, reincidência e priorização) e recebe arquivos novos pela importação.

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

## Carregar os dados

O painel lê a base analítica do PostgreSQL. Depois das migrações, baixe o dataset do grupo para `data/` (ver [docs/dados.md](../docs/dados.md#como-obter-os-dados)) e rode:

```bash
uv run recifeview importar \
  --arquivo ../data/recifeview_demandas_recife_2012_2026.csv.xz \
  --data-do-retrato 2026-10-07 --carga-inicial
```

A carga completa leva alguns minutos, ocupa cerca de 1 GB de disco e aparece como a primeira linha do histórico de importações. O mesmo comando sem `--carga-inicial` importa outro arquivo pelo terminal, e para com aviso se houver algo para decidir: nesse caso, responda pelo painel.

O formulário público sugere as ruas de cada bairro e escreve o endereço como a Central 156 escreve. A lista vem dos arquivos públicos do 156, que têm a coluna de logradouro (o dataset do grupo não tem). Baixe um deles do Drive (`Dados/02_fontes_separadas/bruto`), descompacte em `data/` e rode:

```bash
uv run recifeview carregar-logradouros --arquivo ../data/156_2025.csv
```

O comando aceita `--arquivo` mais de uma vez e guarda só o nome da via e o bairro. Sem essa lista, o formulário funciona, mas sem sugestões e com a comparação de endereço menos precisa.

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
| `API_PASTA_DAS_IMPORTACOES` | Pasta local dos arquivos enviados. Fica fora do git | `../data/importacoes` |
| `API_TAMANHO_MAXIMO_DA_IMPORTACAO_MB` | Limite de tamanho de um arquivo enviado | `800` |
| `API_SAL_DO_ID_LOCAL` | Sal do pseudônimo de endereço. Vazio: registros novos ficam fora da reincidência e os relatos do formulário não se comparam com a base | vem do grupo, nunca do repositório |
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
| `uv run recifeview importar --arquivo ... --data-do-retrato AAAA-MM-DD` | Importa um arquivo pelo terminal |
| `uv run recifeview carregar-logradouros --arquivo ...` | Soma as vias de um arquivo público do 156 à lista do formulário |
| `uv run recifeview --help` | Administração de contas e importação |

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

| `GET /catalogos/filtros` | Anos, RPAs, bairros, categorias e fontes para os filtros |
| `GET /indicadores/visao-geral` | Início: KPIs e volume por fonte |
| `GET /retorno/indicacoes` | Funil, canal de envio, destinos e caminhos das indicações |
| `GET /retorno/ouvidoria` | Canais de entrada e prazo da Ouvidoria |
| `GET /recorrencias` | Local repetido, intervalos e pontos crônicos. `sem_generico=true` tira endereços genéricos |
| `GET /prazos` | Percentis, faixas, categorias e estoque aberto. `sem_mesmo_dia=true` tira os fechados no dia |
| `GET /territorio/bairros` | Taxas por bairro, faixas e tendência |
| `GET /prioridade/criterios` | Critérios do índice e julgamentos propostos pelo grupo |
| `POST /prioridade/indice` | Pesos, razão de consistência, índice dos bairros e sensibilidade |
| `POST /prioridade/fila` | Registros em aberto classificados, com sorteio |
| `GET /war-room/calendario` | Dias disponíveis para a War Room |
| `GET /war-room/dia` | Estado de um dia: entradas, estoque, fila e alertas |
| `GET /sobre` | Cobertura por fonte e ano e correções aplicadas |
| `GET /importacoes` | Histórico, com busca e filtros |
| `POST /importacoes?nome=...` | Recebe um arquivo. O corpo da requisição é o próprio arquivo |
| `GET /importacoes/campos` | Campos da base para o mapeamento |
| `GET /importacoes/{id}` | Colunas, pendências, prévia e relatório de uma importação |
| `PUT /importacoes/{id}/colunas` | Define a fonte, a data do retrato e o mapeamento |
| `PUT /importacoes/{id}/pendencias` | Responde o que não bateu e valida de novo |
| `POST /importacoes/{id}/confirmar` | Grava na base e atualiza as views |
| `POST /importacoes/{id}/cancelar` | Cancela antes da carga |
| `POST /importacoes/{id}/desfazer` | Desfaz a importação mais recente |
| `GET /importacoes/{id}/registros` | Registros tratados, paginados |
| `GET /contribuicoes/catalogo` | Temas, serviços e bairros do formulário. Público |
| `GET /contribuicoes/logradouros?bairro=...` | Vias conhecidas de um bairro. Público |
| `POST /contribuicoes` | Recebe um relato e diz se ficou novo, somado ou em conferência. Público, com limite de envios |
| `GET /contribuicoes/resumo` | Números da fila de relatos |
| `GET /contribuicoes/ocorrencias` | Ocorrências consolidadas, com endereço, para a gestão |
| `GET /contribuicoes/pares` | Relatos parecidos que esperam decisão |
| `PUT /contribuicoes/pares/{id}` | Decide se a dupla é a mesma ocorrência |
| `POST /contribuicoes/pacotes` | Gera o pacote e abre a importação. Recusa se houver dupla sem decisão |

As rotas públicas de contribuições são as únicas de dados sem sessão, e nenhuma delas devolve relato de outra pessoa. Os filtros das rotas de dados são `periodo_inicio` e `periodo_fim` (`AAAA-MM`, só o ano é usado), `rpa`, `bairro` e `categoria`. Toda rota de dados exige sessão e fica registrada em `app.consulta_auditada`.

Como a autenticação funciona, e por que ela ainda é uma proposta, está na [ADR 0005](../docs/adr/0005-autenticacao-com-jwt-proprio.md).

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `api`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#backend-fastapi). O router valida e chama um caso de uso; o caso de uso aplica as regras do domínio e usa portas; os repositórios SQLAlchemy implementam as portas. O `lint-imports` impede que uma camada interna importe uma externa.

```
app/
  domain/           usuario, sessao, senha, acesso, ahp, prioridade, filtros, uma regra por tela
    importacao/     campos, layouts, privacidade, normalizador, correções, pendências, chaves
    contribuicao/   catálogo, endereço canônico, semelhança, comparação e conferência entre canais
  application/      portas/, sessoes.py
    casos_de_uso/   acesso, importacoes/ (um caso de uso por passo), painel/ (um por tela), contribuicoes/
  infrastructure/   db/, repositories/, auth/, importacao/ (leitores, armazenamento, fila), contribuicoes/
  api/              routers/, schemas/, dependencias.py, erros.py, cookies.py
  main.py           monta a aplicação
  cli.py            administração de contas
migrations/         Alembic
tests/              unidade/, api/, integracao/
```

## Regra de privacidade

Nenhuma rota devolve o texto da SEDEC, `id_local`, coordenada nem o hash da senha, e endereço só aparece nas rotas de contribuições da gestão, para quem revisa o relato. Os schemas de resposta são explícitos justamente para que uma coluna nova no banco não vaze por acidente. Na importação, colunas com dado pessoal são reconhecidas pelo nome e pelo conteúdo, ficam bloqueadas e não têm os valores exibidos; arquivo com esse tipo de coluna é apagado depois da carga, e a API nunca devolve o original. A auditoria guarda o tipo do evento, o usuário e o horário, sem IP e sem o e-mail digitado. Ver [docs/dados.md](../docs/dados.md#privacidade-lgpd) e a [ADR 0007](../docs/adr/0007-importacao-de-arquivos-pelo-painel.md).

## Banco de dados

As migrações ficam nesta pasta, para que o esquema tenha um dono só. Convenções de nomes em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#banco-de-dados-postgresql).

- Schema `app`: `usuario`, `sessao`, `evento_de_acesso`, `importacao`, `consulta_auditada`, `contribuicao` (a quarentena do formulário) e `par_de_contribuicoes` (as duplas do pente fino, com a decisão de cada uma).
- Schema `ouro`: `dim_bairro`, `dim_logradouro`, `fato_demanda`, `fato_demanda_substituida` (versão anterior das linhas atualizadas, para desfazer) e as views materializadas `mv_*`, que reproduzem as tabelas do protótipo em Streamlit ([ADR 0006](../docs/adr/0006-modelo-analitico-no-postgresql.md)).

As views são atualizadas depois de cada importação, com o painel no ar.
