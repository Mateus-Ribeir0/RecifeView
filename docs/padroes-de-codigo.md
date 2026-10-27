# Padrões de código

As regras aqui valem para qualquer código do repositório. A organização em camadas fica em [clean-architecture.md](clean-architecture.md); este documento trata de como escrever o código dentro delas. Quando o formatador ou o linter decidir algo, vale o que ele decidir: não discuta estilo que uma ferramenta resolve.

## Clean Code

O código vai ser lido por sete pessoas e avaliado por professores. Ele precisa ser entendido sem que o autor esteja do lado.

### Nomes

- O nome diz o que a coisa é ou faz, sem precisar de comentário: `dias_ate_atendimento`, não `d` nem `delta`.
- Função é verbo; variável e classe são substantivo: `calcular_percentil_90`, `prazo_mediano`, `PrazoPorServico`.
- Booleano é pergunta: `tem_numero_endereco`, `esta_no_prazo`, `isLoading`.
- Sem abreviação inventada (`qtd_ped_brr`). As siglas do domínio são exceção: `rpa`, `sedec`, `ibge`.
- O mesmo conceito tem o mesmo nome em todas as camadas e nos três containers.

### Funções

- Fazem uma coisa só, e o nome diz qual. Se a descrição precisa de "e", são duas funções.
- Curtas: como referência, até 20 linhas. Passou de 40, divida.
- No máximo 3 parâmetros. Mais que isso, agrupe num objeto (`Filtros`).
- Sem parâmetro booleano que muda o comportamento (`carregar(fonte, True)`). Crie duas funções com nomes claros: `carregar_completo`, `carregar_incremental`.
- Separe consulta de comando: uma função ou devolve um valor ou altera estado, não as duas coisas.
- Sem efeito colateral escondido. Uma função `calcular_*` não grava no banco nem escreve log de negócio.

### Fluxo

- Cláusula de guarda e retorno antecipado em vez de `if` aninhado. No máximo 2 níveis de indentação dentro de uma função.
- Sem `else` depois de `return`.
- Coleção vazia em vez de `None`/`null` quando o retorno é uma lista.
- Condição complexa vira função ou variável com nome: `if pedido_e_reincidente(pedido):`.

### Erros

- Exceção, não código de erro nem `None` mágico.
- Exceções do domínio com nome do domínio: `PeriodoInvalido`, `FonteDesconhecida`. A camada de entrada as traduz para HTTP.
- Não engula exceção: trate, registre ou deixe subir. `except: pass` não passa em revisão.
- Valide na borda (router, adaptador de fonte) e confie nos dados dentro do domínio.

### Valores

- Sem número mágico. Limiares viram constantes nomeadas no domínio: `POPULACAO_MINIMA_PER_CAPITA = 1000`, `DIAS_MAXIMOS_DUPLICIDADE = 7`. O nome da constante substitui o comentário.
- Sem string mágica para categorias fixas. Use `Enum` no Python e union de literais no TypeScript (`Fonte`, `Iniciativa`, `Situacao`).
- Prefira valores imutáveis: `dataclass(frozen=True)`, `readonly`, `const`.

### Duplicação e abstração

- Não duplique regra de negócio: a definição de reincidência existe num lugar só.
- Mas não abstraia cedo. Duas ocorrências parecidas podem ser coincidência; na terceira, extraia.
- Composição antes de herança.
- SOLID como guia, não como cerimônia: responsabilidade única e inversão de dependência são as que mais importam aqui (ver [clean-architecture.md](clean-architecture.md)).

### Módulos

- Um arquivo, uma responsabilidade. Como referência, até 300 linhas.
- Exporte o mínimo. O que é detalhe interno fica privado (`_nome` no Python, sem `export` no TypeScript).

### Higiene

- Sem código morto nem bloco comentado: o git guarda o histórico.
- Sem `print` ou `console.log` esquecido. Use o logger.
- Regra do escoteiro: deixe o arquivo um pouco melhor do que encontrou, mas em commit separado (`refactor` ou `style`) se não tiver relação com a tarefa.

## Comentários

**Por padrão, não comente.** O código se explica pelos nomes, pela estrutura e pelos testes. Antes de escrever um comentário, tente nesta ordem:

1. Renomear a variável ou a função.
2. Extrair uma função com nome que diga o que o trecho faz.
3. Extrair uma constante com nome que diga o que o valor significa.
4. Escrever um teste que documente o comportamento.

Comentário só entra quando for indispensável para entender o **porquê** e o código não conseguir expressar isso. Exemplos legítimos:

- Contorno de defeito da fonte que pareceria um erro: `# a Ouvidoria publica resposta antes do registro em 2024 e 2025 (docs/dados.md)`.
- Decisão contraintuitiva que alguém tentaria "consertar": `# mediana, não média: a cauda de drenagem passa de 700 dias`.

Nunca:

- Comentário que repete o código (`# soma os valores`).
- Bloco de código comentado.
- `TODO` sem issue (`TODO(#42): ...` é aceito).
- Comentário de seção ou divisória (`# ===== HELPERS =====`). Se o arquivo precisa de seções, ele precisa ser dividido.
- Histórico de alterações, autor ou data em comentário. Isso é papel do git.
- Docstring que repete a assinatura. Docstring só em função pública cujo contrato não fica claro pelo nome e pelos tipos.

A descrição das rotas para a documentação OpenAPI vai nos parâmetros `summary` e `description` do decorador do FastAPI, não em comentário.

## Travessão

Não use travessão (—) nem meia-risca (–) em nada que faça parte da aplicação: texto de interface, strings, mensagens de erro, logs, comentários, nomes de arquivo, mensagens de commit e documentação.

| Em vez de | Use |
|---|---|
| `2021–2025` | `2021 a 2025` |
| `Prazos — por serviço` | `Prazos por serviço` ou `Prazos: por serviço` |
| `RPA 3 — Norte` | `RPA 3 (Norte)` ou `RPA 3, Norte` |
| `Carregando — aguarde` | `Carregando...` |

Hífen comum (-) continua valendo em palavras compostas (`guarda-chuva`), datas ISO (`2026-10`) e nomes de arquivo em kebab-case. Para conferir antes de commitar:

```bash
git diff --staged | grep -nE '^\+.*[—–]'
```

## Nomes e idioma

| O quê | Idioma | Exemplo |
|---|---|---|
| Conceitos e ações do domínio (variáveis, funções, casos de uso, entidades) | Português, sem acento, igual ao [dicionário de colunas](dados.md#colunas-principais) | `bairro_oficial`, `listar_prazos_por_servico`, `Filtros` |
| Papéis técnicos (sufixos, pastas de camada, convenções de framework) | Inglês | `PrazoRepository`, `routers/`, `domain/`, `useFiltrosGlobais` |
| Comentários (quando inevitáveis) e docstrings | Português | |
| Texto de interface | Português do Brasil, ver [design-system.md](design-system.md#texto-e-voz) | |

Não traduza papel técnico (`RepositorioDePrazo`) nem anglicize conceito de domínio (`neighborhood`, `get_deadlines`).

## Python (backend e processor)

- Formatação e lint com Ruff. Linha de 100 caracteres.
- Type hints em toda função pública, checados com mypy.
- `snake_case` para funções, variáveis e módulos; `PascalCase` para classes; `UPPER_SNAKE_CASE` para constantes.
- Entidades e objetos de valor do domínio como `dataclass(frozen=True)`. Pydantic fica na camada de entrada (schemas) e nas settings.
- Portas como `typing.Protocol`.
- Configuração lida num único módulo de settings (Pydantic Settings). Nada de `os.environ` espalhado.
- Datas sempre com fuso explícito: armazenar em UTC e exibir em `America/Recife`.
- Schema de resposta explícito em toda rota (`response_model`). Nunca devolva um modelo do ORM direto.
- Consultas pesadas usam views materializadas.
- No Processor: todo extrator devolve os registros com a procedência (`arquivo_origem`), a carga é idempotente e toda execução registra as contagens de entrada, descarte e saída.

## TypeScript e React (frontend)

- ESLint e Prettier. `strict` ligado no `tsconfig`. Sem `any`: use `unknown` e estreite o tipo.
- Componentes de função com hooks. Um componente por arquivo, com o nome do arquivo igual ao do componente, em `PascalCase`.
- Componente pequeno: se passou de umas 150 linhas ou mistura busca de dados com desenho, divida em componente de apresentação e hook.
- Props tipadas e somente leitura. No máximo umas 5 props; mais que isso indica que o componente faz coisa demais.
- Cores, espaçamentos e fontes só pelos tokens de `ui/theme`. Nada de hexadecimal solto.
- Formatação de número e data só pelas funções de `domain/formatacao.ts`.
- Estado de servidor fica no cache de consultas. Estado de interface fica no componente ou nos filtros globais.

## Banco de dados (PostgreSQL)

- Tabelas e colunas em `snake_case`, em português, no singular quando for entidade (`bairro`, `servico`). As colunas da fato seguem o dicionário de colunas.
- Prefixos: `fato_` para tabelas fato, `dim_` para dimensões, `mv_` para views materializadas.
- Schemas por camada de dados: `raw` (se a decisão for guardar o bruto no banco), `prata`, `ouro` e `app` (usuários e auditoria).
- Toda mudança de esquema passa por migração versionada. Nunca altere o banco à mão.
- Chave primária explícita em toda tabela. Índice em toda coluna usada em filtro global (`ano`, `mes`, `bairro_oficial`, `rpa`, `servico_codigo`, `fonte`).

## API REST

- Prefixo `/api/v1`.
- Recursos em português, minúsculas e kebab-case, alinhados às telas: `/api/v1/territorio/bairros`, `/api/v1/prazos/servicos`, `/api/v1/fluxo-camara`.
- JSON em `snake_case`, com os nomes do domínio.
- Os filtros globais são parâmetros de consulta com os mesmos nomes em todas as rotas: `periodo_inicio`, `periodo_fim` (`AAAA-MM`), `bairro`, `rpa`, `servico`, `situacao`, `fonte`.
- Toda resposta analítica traz a procedência junto com o dado:

```json
{
  "dados": [],
  "meta": {
    "fonte": ["156_EMLURB"],
    "periodo": { "inicio": "2021-01", "fim": "2025-12" },
    "filtros": { "rpa": 3 },
    "n": 128344,
    "atualizado_em": "2026-10-26T03:00:00Z"
  }
}
```

- Erros no formato `{"erro": {"codigo": "...", "mensagem": "..."}}`, com o status HTTP certo (400, 401, 403, 404, 422, 500).
- Listas longas são paginadas (`limite`, `deslocamento`).
- A documentação OpenAPI gerada pelo FastAPI é o contrato. Os tipos de `infrastructure/api` no frontend batem com ela.

## Configuração e segredos

- Cada pasta tem um `.env.example` com todas as variáveis e valores falsos seguros. O `.env` real nunca é commitado.
- Variáveis em `UPPER_SNAKE_CASE`, com prefixo por container quando houver ambiguidade (`API_`, `PROCESSOR_`).
- O sal do `id_local` vem do gerenciador de segredos em produção e de variável de ambiente local. Nunca de arquivo versionado.

## Testes

- A distribuição por camada está em [clean-architecture.md](clean-architecture.md#testes-por-camada).
- Teste o que tem regra: percentil, per capita, reincidência, filtros, formatação, pseudonimização.
- Estrutura preparar, agir, verificar, com um comportamento por teste.
- Testes rápidos, independentes entre si, repetíveis e sem depender de ordem.
- Fixtures com dados sintéticos pequenos, criados para o teste. Nunca uma amostra do dataset real, e muito menos texto da SEDEC.
- Teste de regressão para todo bug corrigido.
- O nome do teste descreve o comportamento, em português: `test_reincidencia_ignora_registro_sem_numero`. Um bom nome dispensa comentário no teste.

## Logs

- Logs estruturados (JSON) no backend e no processor.
- Nunca registre: texto da SEDEC, `id_local` junto com coordenada, token, senha ou conteúdo de `.env`.
- Registre: rota, filtros, duração, contagens e erros com stack trace.
- Mensagens de log seguem a regra do travessão.
