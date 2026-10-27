# Como contribuir

Este guia vale para todo mundo que mexe no repositório, pessoa ou assistente de código. Ele existe para que o histórico do git conte a história do projeto sem precisar de explicação extra, e para que qualquer integrante consiga rodar o projeto a partir do README.

## Fluxo de trabalho

1. Atualize a `main` local: `git switch main && git pull`.
2. Crie uma branch a partir dela, seguindo o padrão abaixo.
3. Faça commits pequenos, cada um com um assunto só.
4. Antes de abrir o PR, confira a [definição de pronto](#definição-de-pronto).
5. Abra o pull request usando o modelo e peça revisão de pelo menos uma pessoa do grupo.
6. Faça o merge com **squash** quando o PR tiver commits de ajuste ("corrige typo do commit anterior") e com **rebase** quando os commits já estiverem limpos e cada um fizer sentido sozinho.

A `main` sempre roda. Nada vai para ela sem passar por PR.

## Branches

```
tipo/descricao-curta-em-kebab-case
```

O `tipo` é o mesmo dos commits. Exemplos:

| Branch | Para quê |
|---|---|
| `feat/mapa-coropletico-bairros` | Nova funcionalidade |
| `fix/prazo-negativo-ouvidoria` | Correção |
| `docs/readme-processor` | Só documentação |
| `build/configura-vite` | Ferramentas de build e dependências |
| `refactor/servico-recorrencias` | Reestruturação sem mudar comportamento |

Use uma branch por assunto. Se aparecer outro assunto no meio do caminho, abra outra branch.

## Commits

O grupo segue [Conventional Commits 1.0](https://www.conventionalcommits.org/pt-br/v1.0.0/), com a descrição em português.

### Formato

```
tipo(escopo): descrição curta

Corpo opcional explicando o porquê da mudança, não o como.
Quebre as linhas em 72 caracteres.

Refs: #12
```

### Regras da primeira linha

- No máximo 72 caracteres.
- Verbo no imperativo, na terceira pessoa do presente, como se completasse a frase "este commit...": `adiciona`, `corrige`, `remove`, `atualiza`, `extrai`.
- Tudo em minúsculas, exceto nomes próprios e siglas (`RPA`, `SEDEC`, `README`).
- Sem ponto final.
- Sem emoji e sem travessão (— ou –).
- Diz **o que** muda para quem lê o histórico, não qual arquivo foi tocado.

### Tipos

| Tipo | Quando usar |
|---|---|
| `feat` | Funcionalidade nova para quem usa o sistema (tela, rota, indicador, fonte de dados nova) |
| `fix` | Correção de comportamento errado |
| `docs` | Só documentação (README, `docs/`, comentários de documentação) |
| `style` | Formatação, espaços, ordem de imports; nenhuma mudança de comportamento |
| `refactor` | Mudança de estrutura interna sem mudar comportamento nem corrigir bug |
| `perf` | Melhora de desempenho |
| `test` | Adiciona ou corrige testes |
| `build` | Dependências, configuração de build, Docker, gerenciador de pacotes |
| `ci` | Pipelines de integração contínua |
| `chore` | Manutenção que não se encaixa acima (`.gitignore`, `.editorconfig`, renomear pasta) |
| `revert` | Desfaz um commit anterior |

### Escopos

| Escopo | Abrange |
|---|---|
| `frontend` | `frontend/` |
| `backend` | `backend/`, exceto migrações |
| `processor` | `processor/` |
| `db` | Esquema, migrações, views e índices do PostgreSQL |
| `infra` | AWS, EventBridge, Docker Compose, deploy |
| `adr` | Registros de decisão em `docs/adr/` |
| `repo` | Configuração do repositório (`.github/`, `.claude/`, `.gitignore`, `.editorconfig`) |

Documentação de uma parte específica usa o escopo dessa parte (`docs(processor): explica a carga incremental`). Documentação geral do projeto vai sem escopo (`docs: atualiza cronograma de entregas`). Fora esse caso, commit sem escopo deve ser raro: geralmente indica que ele precisa ser dividido.

### Mudança que quebra compatibilidade

Use `!` depois do escopo e explique no rodapé:

```
feat(backend)!: muda prefixo das rotas para /api/v1

BREAKING CHANGE: o frontend precisa apontar para o novo prefixo.
```

### Como separar commits

Cada commit deve fazer sentido sozinho e deixar o projeto funcionando. Alguns casos comuns:

| Situação | Commits |
|---|---|
| Instalar o Leaflet e criar o mapa | `build(frontend): adiciona leaflet e react-leaflet` e depois `feat(frontend): adiciona mapa coroplético de demanda por bairro` |
| Criar uma tabela e a rota que lê dela | `feat(db): cria tabela fato_demanda` e depois `feat(backend): adiciona rota de demanda por bairro` |
| Rodar o formatador e corrigir um bug no mesmo arquivo | `style(backend): aplica ruff format` e depois `fix(backend): corrige percentil 90 de prazos` |
| Funcionalidade nova com instruções novas para rodar | O README entra **no mesmo commit** da funcionalidade |

### Exemplos

Bons:

```
feat(processor): adiciona adaptador da Câmara (SAGL)
fix(backend): exclui prazos negativos do cálculo de mediana
docs(adr): registra decisão sobre o armazenamento da camada bruta
build(backend): fixa fastapi e sqlalchemy no pyproject
refactor(frontend): extrai filtros globais para um contexto próprio
test(backend): cobre reincidência sem número de endereço
```

Ruins, e por quê:

| Mensagem | Problema |
|---|---|
| `update` | Não diz o que mudou |
| `feat: várias melhorias no dashboard` | Mais de um assunto no mesmo commit |
| `fix(frontend): Corrigido o bug.` | Particípio, maiúscula, ponto final e não diz qual bug |
| `feat(frontend): altera MapaBairros.tsx` | Fala do arquivo, não do efeito |
| `feat(frontend): adiciona mapa — versão inicial` | Travessão |
| `wip` | Commit de trabalho em andamento não vai para a `main` |

## Pull requests

- Use o modelo em [.github/pull_request_template.md](.github/pull_request_template.md).
- Um PR resolve um assunto. Mire em menos de 400 linhas alteradas, sem contar arquivos gerados.
- O título do PR segue o mesmo formato da primeira linha do commit.
- Mudança visual vai com captura de tela.
- Mudança de dado ou de cálculo informa fonte, período, filtro e o número antes e depois.

## Definição de pronto

Uma mudança está pronta quando:

- [ ] Lint, formatação e testes passam na parte alterada.
- [ ] Cada arquivo está na camada certa e as importações respeitam a regra da dependência ([docs/clean-architecture.md](docs/clean-architecture.md)).
- [ ] O código segue o Clean Code de [docs/padroes-de-codigo.md](docs/padroes-de-codigo.md#clean-code), e os comentários que sobraram são indispensáveis.
- [ ] Não há travessão nem meia-risca em texto de interface, código, log ou commit.
- [ ] Não há segredo, dado pessoal, texto da SEDEC nem arquivo de dados no diff.
- [ ] O README da raiz e o da pasta alterada continuam ensinando a rodar o projeto do zero. Isso inclui dependência nova, variável de ambiente, comando, porta e passo de configuração.
- [ ] O `.env.example` da pasta tem toda variável nova, com um valor de exemplo seguro.
- [ ] Decisão técnica nova está registrada em [docs/adr/](docs/adr/README.md).
- [ ] Todo `.md`, skill, agente ou hook criado, renomeado ou removido está refletido no [MAPA-DO-REPOSITORIO.md](MAPA-DO-REPOSITORIO.md). Para conferir: `bash .claude/hooks/conferir-mapa.sh`.
- [ ] A interface segue [docs/design-system.md](docs/design-system.md).
- [ ] Os commits seguem este guia.

## Versões e entregas

Cada entrega semanal ganha uma tag anotada no commit que foi apresentado:

```
git tag -a semana-13 -m "Entrega da Semana 13: N4 Dashboard Interativo, versão inicial"
```

Assim dá para voltar exatamente ao estado de cada entrega na documentação final (N9) e no SR2.
