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

### Outras origens além do arquivo

A importação também lê de um endereço na internet e de um banco externo, pelo painel ou pelo terminal ([ADR 0012](../docs/adr/0012-origens-de-dados-alem-do-arquivo.md)). Os dois caminhos entregam um arquivo ao mesmo fluxo: colunas, pendências, pente fino, carga e desfazer.

- **Endereço:** só `https` e só os hosts de `API_HOSTS_DE_IMPORTACAO` (por padrão, o portal de dados abertos do Recife). Redirecionamento para outro host é recusado.
- **Banco:** só as conexões de `API_BANCOS_DE_ORIGEM` (hoje, PostgreSQL). A consulta precisa começar com `SELECT` ou `WITH`, roda em transação só de leitura e para depois de `API_SEGUNDOS_DA_EXTRACAO`.

```bash
uv run recifeview importar --endereco "https://dados.recife.pe.gov.br/<caminho do arquivo>.csv" \
  --data-do-retrato 2026-11-11
uv run recifeview importar --banco sgde --consulta "SELECT * FROM demandas WHERE ano = 2026" \
  --data-do-retrato 2026-11-11
```

É assim que o agendador (cron ou EventBridge) traz os arquivos novos enquanto o Processor não existe. A importação do arquivo da Ouvidoria pelo portal também traz o protocolo de cada manifestação, que alimenta a consulta pública pelo protocolo.

O formulário público sugere as ruas de cada bairro e escreve o endereço como a Central 156 escreve. A lista vem dos arquivos públicos do 156, que têm a coluna de logradouro (o dataset do grupo não tem). Baixe um deles do Drive (`Dados/02_fontes_separadas/bruto`), descompacte em `data/` e rode:

```bash
uv run recifeview carregar-logradouros --arquivo ../data/156_2025.csv
```

O comando aceita `--arquivo` mais de uma vez e guarda só o nome da via e o bairro. Sem essa lista, o formulário funciona, mas sem sugestões e com a comparação de endereço menos precisa.

## Contas de acesso

Existem três tipos de conta ([ADR 0010](../docs/adr/0010-contas-de-cidadao-e-niveis-de-acesso.md) e [ADR 0013](../docs/adr/0013-acesso-corporativo-dos-orgaos.md)):

- **Gestão** (`GESTOR` e `ADMINISTRADOR`): criadas pela linha de comando abaixo. Veem o painel, o pente fino, a importação e os encaminhamentos. Só o `ADMINISTRADOR` cria, edita, desativa e exclui acessos corporativos; o `GESTOR` vê a lista.
- **Corporativo** (`CORPORATIVO`): uma pessoa de um órgão (Emlurb, Compesa, Neoenergia e os demais do catálogo), criada pela administração na tela "Acessos corporativos". A conta nasce sem senha e recebe por e-mail um convite com o link `/convite/<token>`, de uso único e válido por 7 dias, em que a pessoa define a senha e já entra. Vê só os encaminhamentos feitos ao próprio órgão e responde a eles em `/corporativo`.
- **Cidadão** (`CIDADAO`): criadas pela própria pessoa em `/cadastrar`, sem confirmação por e-mail: o cadastro já abre a sessão. Veem os relatos da cidade (sem número exato nem texto), os próprios relatos com a situação de cada um e os indicadores do bairro.

Cada perfil abre só a sua área: as rotas da gestão respondem 403 para o cidadão e o corporativo, as de `/corporativo` respondem 403 para a gestão e o cidadão, e as de `/cidade` exigem conta de cidadão.

Sem servidor SMTP configurado, os e-mails da API (código de "Esqueci minha senha", convite do acesso corporativo e avisos do ciclo) não são enviados: viram arquivos `.txt` na pasta de `API_PASTA_DOS_EMAILS` (padrão `../data/emails`, fora do git). Abra o arquivo mais recente para ver o código ou o link do convite. Para os e-mails chegarem na caixa de entrada, configure o SMTP (seção abaixo).

### Enviar os e-mails de verdade (SMTP)

A API envia por qualquer servidor SMTP. O provedor definitivo do projeto ainda está em aberto ([ADR 0010](../docs/adr/0010-contas-de-cidadao-e-niveis-de-acesso.md)), então use uma conta de teste sua. Com Gmail:

1. Ative a verificação em duas etapas na conta Google.
2. Crie uma senha de app em https://myaccount.google.com/apppasswords. O Google mostra 16 letras.
3. No `backend/.env`, preencha (a senha sem espaços):

```bash
API_SMTP_SERVIDOR=smtp.gmail.com
API_SMTP_PORTA=587
API_SMTP_SEGURANCA=starttls
API_SMTP_USUARIO=seu.endereco@gmail.com
API_SMTP_SENHA=abcdefghijklmnop
```

4. Reinicie a API. No início do log aparece `E-mails saem pelo servidor SMTP smtp.gmail.com`.

Outros provedores funcionam do mesmo jeito: Outlook (`smtp.office365.com`, 587, `starttls`), Brevo (`smtp-relay.brevo.com`, 587) ou Amazon SES (endpoint SMTP da região, 587). Se o servidor recusar o envio, o pedido de nova senha responde 503 com `envio_de_email_indisponivel`, nada é gravado e o log diz o motivo (usuário e senha recusados ou servidor fora do ar), sem o conteúdo da mensagem.

> O `.env` não vai para o git. Nunca coloque a senha do SMTP em outro arquivo, em issue ou em mensagem do grupo.

As contas criadas pela linha de comando nascem com uma senha temporária que precisa ser trocada no primeiro acesso.

```bash
uv run recifeview cadastrar-usuario --email nome@recife.pe.gov.br --nome "Nome Completo"
uv run recifeview cadastrar-usuario --email outra@recife.pe.gov.br --nome "Outra Pessoa" --perfil ADMINISTRADOR
uv run recifeview cadastrar-usuario --email equipe@compesa.exemplo --nome "Equipe Compesa" --perfil CORPORATIVO --orgao COMPESA
uv run recifeview mudar-perfil --email nome@recife.pe.gov.br --perfil ADMINISTRADOR
uv run recifeview redefinir-senha --email nome@recife.pe.gov.br
```

A senha temporária aparece uma única vez no terminal. Entregue por um canal seguro. `redefinir-senha` também desbloqueia a conta e derruba as sessões abertas. `mudar-perfil` só troca entre `GESTOR` e `ADMINISTRADOR`. A conta corporativa pela linha de comando serve ao ambiente local; em uso real, a administração cria pela tela, com convite.

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
| `API_PASTA_DOS_EMAILS` | Onde os e-mails de conta são gravados quando não há SMTP configurado. Fica fora do git | `../data/emails` |
| `API_SMTP_SERVIDOR` | Servidor SMTP. Vazio: os e-mails ficam na pasta acima | `smtp.gmail.com` |
| `API_SMTP_PORTA` | Porta do servidor SMTP | `587` |
| `API_SMTP_SEGURANCA` | `starttls` (porta 587) ou `ssl` (porta 465) | `starttls` |
| `API_SMTP_USUARIO` | Usuário do SMTP. Vazio: envia sem autenticar | `seu.endereco@gmail.com` |
| `API_SMTP_SENHA` | Senha do SMTP (no Gmail, a senha de app). Nunca entra no repositório | vem de você, só no `.env` |
| `API_SMTP_REMETENTE` | Endereço do remetente. Vazio: usa o `API_SMTP_USUARIO` | `avisos@exemplo.com` |
| `API_SAL_DO_ID_LOCAL` | Sal do pseudônimo de endereço. Vazio: registros novos ficam fora da reincidência e os relatos do formulário não se comparam com a base | vem do grupo, nunca do repositório |
| `API_ENDERECO_DO_SITE` | Endereço público do site, usado no link de retorno que vai na mensagem ao órgão | `http://localhost:5173` |
| `API_PASTA_DOS_ENCAMINHAMENTOS` | Onde ficam as mensagens dos órgãos sem canal configurado. Fica fora do git | `../data/encaminhamentos` |
| `API_CANAIS_DOS_ORGAOS` | Canal de cada órgão, em JSON (ver [Encaminhar ao órgão](#encaminhar-ao-órgão)). Vazio: todos na pasta acima | `{}` |
| `API_HOSTS_DE_IMPORTACAO` | Hosts de onde a importação pode baixar, em JSON | `["dados.recife.pe.gov.br"]` |
| `API_BANCOS_DE_ORIGEM` | Conexões de leitura para a importação por banco, em JSON (nome e URL). A URL tem senha: só no `.env` | `{}` |
| `API_SEGUNDOS_DA_EXTRACAO` | Tempo máximo de uma consulta ao banco externo | `120` |
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
| `uv run recifeview importar --arquivo ... --data-do-retrato AAAA-MM-DD` | Importa um arquivo pelo terminal. Troque `--arquivo` por `--endereco URL` ou por `--banco NOME --consulta SQL` para as outras origens |
| `uv run recifeview carregar-logradouros --arquivo ...` | Soma as vias de um arquivo público do 156 à lista do formulário |
| `uv run recifeview encaminhar-prioritarias --fonte 156 --nota-minima 7 --limite 20` | Encaminha ao órgão sugerido as ocorrências de nota alta sem encaminhamento aberto. Feito para o agendador (cron ou EventBridge) |
| `uv run recifeview lembrar-orgaos` | Lembra o órgão de cada encaminhamento com prazo vencido sem resposta final: no sino das contas corporativas do órgão e, se ele tiver canal configurado, numa mensagem com link novo. Um lembrete por encaminhamento. Feito para o agendador, uma vez por dia |
| `uv run recifeview mudar-perfil --email ... --perfil ADMINISTRADOR` | Troca o perfil de uma conta da gestão entre `GESTOR` e `ADMINISTRADOR` |
| `uv run recifeview --help` | Administração de contas e importação |

## Encaminhar ao órgão

A tela de Prioridade sugere para qual órgão cada ocorrência vai, e a gestão confirma ([ADR 0011](../docs/adr/0011-encaminhamento-ao-orgao-e-retorno.md)). A mensagem sai pelo canal configurado em `API_CANAIS_DOS_ORGAOS`. Os órgãos aceitos são `EMLURB`, `COMPESA`, `NEOENERGIA`, `CTTU`, `DEFESA_CIVIL`, `SEINFRA`, `URB`, `SAUDE`, `MEIO_AMBIENTE` e `ORDEM_PUBLICA`.

| Canal | Como configurar | O que acontece |
|---|---|---|
| `local` (padrão) | Nada | A mensagem vira um arquivo JSON em `API_PASTA_DOS_ENCAMINHAMENTOS` |
| `plataforma` | Nada: vale para o órgão sem canal configurado que tem acesso corporativo ativo | Nenhuma mensagem externa: as pessoas do órgão recebem a ocorrência no sino e por e-mail e respondem em `/corporativo` |
| `email` | `{"canal": "email", "destino": "endereco@orgao"}` | Sai pelo SMTP das contas (ou fica na caixa de e-mails local, sem SMTP) |
| `webhook` | `{"canal": "webhook", "destino": "https://...", "token": "..."}` | `POST` do JSON abaixo no endereço, com `Authorization: Bearer <token>` quando houver token |

Corpo enviado ao webhook (e guardado no arquivo local, em `dados`):

```json
{
  "codigo": "ENC-2026-000001",
  "orgao": "COMPESA",
  "fonte": "OUVIDORIA",
  "protocolo_de_origem": "2026/0001",
  "data_abertura": "2026-09-01",
  "categoria": "DRENAGEM",
  "servico": "LIMPEZA DE GALERIAS E VALETAS",
  "bairro_oficial": "AFOGADOS",
  "rpa": "5",
  "situacao_na_fonte": "ABERTA",
  "nota": 8.4,
  "justificativa": "Terceiro pedido no mesmo ponto",
  "prazo_de_resposta": "2026-12-11",
  "link_de_retorno": "http://localhost:5173/retorno/<token>"
}
```

### Quem é avisado

Cada aviso vira uma notificação no sino da plataforma (`app.notificacao`) e, para quem não desligou os avisos, um e-mail pela mesma via dos e-mails de conta (SMTP, ou arquivos em `API_PASTA_DOS_EMAILS` sem SMTP). A falha de um e-mail fica no log e não desfaz a mudança.

| Quando | Quem recebe |
|---|---|
| O órgão responde (pela área corporativa ou pelo link) | A pessoa da gestão que encaminhou |
| O encaminhamento é enviado, recebido, resolvido ou devolvido, ou o órgão atualiza o andamento | O cidadão com conta que guardou o protocolo em "Meus pedidos" ou que enviou relato somado à ocorrência, com a resposta ao cidadão e a previsão |
| Uma ocorrência é encaminhada ao órgão | As contas corporativas ativas do órgão |
| O prazo vence sem resposta final | As contas corporativas do órgão e, se houver, o canal configurado, pelo comando `recifeview lembrar-orgaos` |

O órgão responde pela área corporativa, abrindo o link ou, se tiver sistema, com `POST /api/v1/retornos` e `{"token": "<token do link>", "situacao": "resolvido", "protocolo_do_orgao": "...", "observacao": "...", "resposta_ao_cidadao": "...", "previsao": "AAAA-MM-DD"}`. A observação é interna (gestão e órgão); a resposta ao cidadão é a única parte que chega a quem pediu. A previsão só vale com `recebido`, que pode ser repetido para atualizar o andamento. Se o canal falhar, o encaminhamento fica como `falhou` e o painel oferece o reenvio.

## Rotas

Todas sob `/api/v1`. Os erros seguem o formato `{"erro": {"codigo", "mensagem", "detalhes"}}`, descrito em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#api-rest).

| Método e caminho | O que faz |
|---|---|
| `GET /saude` | Confirma que a API está no ar |
| `POST /autenticacao/entrar` | Recebe e-mail e senha; devolve o token de acesso e grava o cookie de sessão |
| `POST /autenticacao/renovar` | Emite um token de acesso novo a partir do cookie de sessão |
| `POST /autenticacao/sair` | Encerra a sessão e apaga o cookie |
| `GET /autenticacao/eu` | Devolve o usuário do token de acesso |
| `POST /contas` | Cria uma conta de cidadão e já abre a sessão. E-mail que já tem conta volta como erro no campo `email` |
| `POST /contas/recuperar-senha` | Envia um código para nova senha (contas de cidadão e corporativas) |
| `POST /contas/nova-senha` | Troca a senha com o código e derruba as sessões |
| `PUT /contas/eu` | Atualiza nome e bairro |
| `PUT /contas/eu/avisos` | Liga ou desliga os avisos por e-mail do andamento de pedidos, relatos e encaminhamentos |
| `POST /contas/eu/excluir` | Exclui a conta de cidadão, com a senha |
| `GET /cidade/ocorrencias` | Relatos dos últimos 90 dias, com rua só da lista oficial e número em faixa de centena |
| `GET /cidade/meus-relatos` | Os relatos que a própria pessoa enviou com a conta aberta, com endereço e situação. A de um relato somado é a da ocorrência que o recebeu. Se a ocorrência foi encaminhada, traz o órgão e as etapas |
| `GET /cidade/pedidos` | Os protocolos que a pessoa guardou, com o andamento e o encaminhamento de cada um |
| `POST /cidade/pedidos` | Guarda um protocolo para acompanhar (até 20 por conta) |
| `DELETE /cidade/pedidos/{id}` | Deixa de acompanhar um protocolo |
| `POST /publico/pedidos/consultar` | Andamento de um pedido pelo protocolo, sem conta: situação na fonte e, se houver, o órgão para o qual foi encaminhado e a etapa. O protocolo vai no corpo |
| `GET /publico/bairros/{bairro}` | Indicadores do bairro comparados com o Recife, sem conta |
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
| `GET /importacoes/origens` | Hosts permitidos e conexões de banco configuradas (só o nome) |
| `POST /importacoes/por-endereco` | Baixa o arquivo de um endereço permitido e abre a importação |
| `POST /importacoes/por-banco` | Roda uma consulta só de leitura numa conexão configurada e abre a importação |
| `GET /importacoes/{id}` | Colunas, pendências, prévia e relatório de uma importação |
| `PUT /importacoes/{id}/colunas` | Define a fonte, a data do retrato e o mapeamento |
| `PUT /importacoes/{id}/pendencias` | Responde o que não bateu e valida de novo |
| `POST /importacoes/{id}/confirmar` | Grava na base e atualiza as views |
| `POST /importacoes/{id}/cancelar` | Cancela antes da carga |
| `POST /importacoes/{id}/desfazer` | Desfaz a importação mais recente |
| `GET /importacoes/{id}/registros` | Registros tratados, paginados |
| `GET /contribuicoes/catalogo` | Temas, serviços e bairros do formulário. Público |
| `GET /contribuicoes/logradouros?bairro=...` | Vias conhecidas de um bairro. Público |
| `POST /contribuicoes` | Recebe um relato e diz se ficou novo, somado ou em conferência. Público, com limite de envios. Com token de conta de cidadão, o relato fica ligado a ela para aparecer em "Meus relatos" |
| `GET /contribuicoes/resumo` | Números da fila de relatos |
| `GET /contribuicoes/ocorrencias` | Ocorrências consolidadas, com endereço, para a gestão. A que já está na base traz a `chave_registro` para encaminhar e o último encaminhamento |
| `GET /contribuicoes/pares` | Relatos parecidos que esperam decisão |
| `PUT /contribuicoes/pares/{id}` | Decide se a dupla é a mesma ocorrência |
| `POST /contribuicoes/pacotes` | Gera o pacote e abre a importação. Recusa se houver dupla sem decisão |
| `GET /encaminhamentos` | Resumo (abertos, atrasados, por situação, mediana até resolver) e lista. Filtros `situacao`, `orgao`, `so_atrasados` e `pedem_acao` (devolução sem novo destino, falha de envio ou prazo vencido, no último encaminhamento de cada ocorrência) |
| `GET /encaminhamentos/orgaos` | Órgãos que recebem encaminhamentos e o canal configurado de cada um |
| `GET /encaminhamentos/ocorrencias/{chave_registro}` | Prepara o encaminhamento: a ocorrência, a sugestão de destino com a distribuição do tema e o histórico |
| `POST /encaminhamentos` | Encaminha a ocorrência ao órgão escolhido e manda a mensagem pelo canal dele. Para uma ocorrência do formulário, aceita `contribuicao_id`: a mensagem leva a rua oficial e a faixa de numeração do relato |
| `GET /avisos/painel` | Contadores do menu: devoluções sem novo destino, falhas, prazos vencidos e duplas esperando o pente fino |
| `GET /encaminhamentos/desempenho` | Compara os órgãos: encaminhados, abertos, vencidos, resolvidos no prazo, mediana até resolver, devolvidos, o que voltou a ser pedido em 30 dias, canal e acessos ativos; série de 12 semanas e grupos do mesmo problema |
| `GET /encaminhamentos/{id}` | Detalhe com os eventos do ciclo, os encaminhamentos do mesmo problema e quantos registros da base têm o mesmo local e tema em 30 dias |
| `POST /encaminhamentos/{id}/retorno` | A gestão registra o que o órgão respondeu por outro meio |
| `POST /encaminhamentos/{id}/reenvio` | Reenvia depois de uma falha do canal, com link novo |
| `POST /retornos/abrir` | O órgão vê o que recebeu. Público: o token do link vai no corpo |
| `POST /retornos` | O órgão marca `recebido`, `resolvido` ou `devolvido`, com o protocolo dele, a resposta ao cidadão e a previsão. Público, para pessoa ou sistema |
| `GET /acessos-corporativos` | Contas corporativas com o órgão e a situação (convite enviado, convite vencido, ativo, desativado). Gestão |
| `POST /acessos-corporativos` | Cria o acesso de um órgão e manda o convite. Só `ADMINISTRADOR` |
| `PUT /acessos-corporativos/{id}` | Corrige nome ou órgão. Só `ADMINISTRADOR` |
| `POST /acessos-corporativos/{id}/convite` | Manda um convite novo, que invalida o anterior. Só `ADMINISTRADOR` |
| `POST /acessos-corporativos/{id}/desativacao` e `/reativacao` | Desativa (derruba as sessões) ou reativa. Só `ADMINISTRADOR` |
| `DELETE /acessos-corporativos/{id}` | Exclui o acesso: apaga nome e e-mail e mantém a auditoria. Só `ADMINISTRADOR` |
| `POST /convites/abrir` | Mostra para quem é o convite. Público: o token vai no corpo |
| `POST /convites/aceitar` | Define a senha do acesso corporativo e abre a sessão. Público |
| `GET /corporativo/painel` | Visão geral do órgão: números do ciclo, abertas por bairro, 12 semanas, as mais urgentes, grupos do mesmo problema e pessoas com retorno |
| `GET /corporativo/ocorrencias` | Fila do órgão por `aba` (`novas`, `em_atendimento`, `vencidas`, `resolvidas`, `devolvidas`, `todas`), com filtros `bairro` e `categoria`. Cada item traz o mesmo problema no órgão e fora dele e quantas pessoas acompanham, sem o protocolo |
| `GET /corporativo/ocorrencias/{id}` | Detalhe de uma ocorrência do órgão, com o protocolo de origem, os eventos e o mesmo problema. De outro órgão, 404 |
| `POST /corporativo/ocorrencias/{id}/resposta` | Em atendimento (com previsão), resolvida ou devolvida, com a resposta ao cidadão (obrigatória para resolver e devolver). `tambem` aplica a mesma resposta a até 20 ocorrências do mesmo problema, tudo ou nada |
| `GET /corporativo/dados` | O que a base aberta registra com o nome do órgão, por ano e fonte, bairro, tema e situação. Filtros `ano_inicio` e `ano_fim` |
| `GET /notificacoes` | As 30 notificações mais recentes da conta e quantas não foram lidas. Qualquer perfil |
| `POST /notificacoes/{id}/leitura` e `POST /notificacoes/leitura` | Marca uma ou todas como lidas |

O `POST /autenticacao/entrar` aceita `area` (`cidade`, `gestao` ou `corporativo`): pela porta da gestão, só entra conta da gestão, e pela corporativa, só conta corporativa; as outras recebem 403. As rotas de `/contas` que mandam e-mail têm limite de 10 chamadas a cada 10 minutos por origem. As rotas de painel, importações, pente fino, encaminhamentos e acessos corporativos exigem conta da gestão, e as de `/corporativo`, conta corporativa. As rotas públicas de contribuições, de retorno do órgão e de `/publico` são as únicas de dados sem sessão: nenhuma delas devolve relato de outra pessoa, endereço ou texto; as de retorno e de convite só abrem com o token do link; e as de retorno, de convite e de `/publico` têm limite de 30 chamadas a cada 10 minutos por origem. Os filtros das rotas de dados são `periodo_inicio` e `periodo_fim` (`AAAA-MM`, só o ano é usado), `rpa`, `bairro` e `categoria`. Toda rota de dados exige sessão e fica registrada em `app.consulta_auditada`.

Como a autenticação funciona, e por que ela ainda é uma proposta, está na [ADR 0005](../docs/adr/0005-autenticacao-com-jwt-proprio.md).

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `api`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#backend-fastapi). O router valida e chama um caso de uso; o caso de uso aplica as regras do domínio e usa portas; os repositórios SQLAlchemy implementam as portas. O `lint-imports` impede que uma camada interna importe uma externa.

```
app/
  domain/           usuario, sessao, senha, acesso, ahp, prioridade, filtros, uma regra por tela
    importacao/     campos, layouts, privacidade, normalizador, correções, pendências, chaves
    contribuicao/   catálogo, endereço canônico, semelhança, comparação e conferência entre canais
    encaminhamento/ órgãos, sugestão de destino, ciclo, mensagem, avisos, mesmo problema e desempenho
  application/      portas/, sessoes.py
    casos_de_uso/   acesso, importacoes/ (um caso de uso por passo), painel/ (um por tela), contribuicoes/,
                    encaminhamentos/, acessos_corporativos/ (cadastro e convite), corporativo/ (área do órgão)
  infrastructure/   db/, repositories/, auth/, importacao/ (leitores, armazenamento, fila), contribuicoes/,
                    encaminhamento/ (caixa local, e-mail, webhook e o despacho por órgão)
  api/              routers/, schemas/, dependencias.py, erros.py, cookies.py
  main.py           monta a aplicação
  cli.py            administração de contas
migrations/         Alembic
tests/              unidade/, api/, integracao/
```

## Regra de privacidade

Nenhuma rota devolve o texto da SEDEC, `id_local`, coordenada nem o hash da senha, e endereço só aparece nas rotas de contribuições da gestão, para quem revisa o relato. A área corporativa vê só o bairro, a RPA e, no relato do formulário, a rua oficial com a faixa de numeração; de quem acompanha o pedido, só a contagem; e o protocolo só no detalhe, como na mensagem ao órgão. Da ocorrência de outro órgão com o mesmo problema, o corporativo vê só o nome do órgão e a etapa. Os schemas de resposta são explícitos justamente para que uma coluna nova no banco não vaze por acidente. Na importação, colunas com dado pessoal são reconhecidas pelo nome e pelo conteúdo, ficam bloqueadas e não têm os valores exibidos; arquivo com esse tipo de coluna é apagado depois da carga, e a API nunca devolve o original. A auditoria guarda o tipo do evento, o usuário e o horário, sem IP e sem o e-mail digitado. Ver [docs/dados.md](../docs/dados.md#privacidade-lgpd) e a [ADR 0007](../docs/adr/0007-importacao-de-arquivos-pelo-painel.md).

## Banco de dados

As migrações ficam nesta pasta, para que o esquema tenha um dono só. Convenções de nomes em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#banco-de-dados-postgresql).

- Schema `app`: `usuario` (com `email_confirmado_em`, `bairro_oficial`, `recebe_avisos` e, na conta corporativa, `orgao`), `convite_de_acesso` (só o hash do token do convite, a validade e o uso), `notificacao` (o sino de cada conta, com a leitura), `codigo_de_conta` (só o hash do código), `sessao`, `evento_de_acesso`, `importacao`, `consulta_auditada`, `contribuicao` (a quarentena do formulário), `par_de_contribuicoes` (as duplas do pente fino, com a decisão de cada uma), `encaminhamento` (cópia do que foi mandado ao órgão, com o pseudônimo do local e o código do serviço para achar o mesmo problema, o hash do token do link, a situação, a data do lembrete e, quando veio do formulário, o relato e o local aproximado), `evento_de_encaminhamento` (cada mudança do ciclo, com autor, nota interna, resposta ao cidadão e previsão) e `pedido_acompanhado` (protocolos que um cidadão guardou).
- Schema `ouro`: `dim_bairro`, `dim_logradouro`, `fato_demanda` (com o `protocolo` quando a fonte o publica), `fato_demanda_substituida` (versão anterior das linhas atualizadas, para desfazer) e as views materializadas `mv_*`, que reproduzem as tabelas do protótipo em Streamlit ([ADR 0006](../docs/adr/0006-modelo-analitico-no-postgresql.md)). A `mv_demanda_por_orgao` conta a base por fonte, ano, nome do órgão na fonte, bairro, tema e situação, sem as ações proativas da Defesa Civil, para a tela "Dados do órgão" ([ADR 0013](../docs/adr/0013-acesso-corporativo-dos-orgaos.md)).

As views são atualizadas depois de cada importação, com o painel no ar.
