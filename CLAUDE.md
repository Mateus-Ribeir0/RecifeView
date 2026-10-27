# RecifeView: instruções para o Claude

Leia este arquivo inteiro antes de qualquer tarefa. Ele é curto de propósito: os detalhes ficam nos documentos linkados abaixo, e o documento da área em que você vai mexer deve ser aberto **antes** de mexer.

## O projeto

RecifeView é o projeto do Grupo 08 de Projetos 5 (CESAR School, 2026.2, trilha de Análise e Visualização de Dados). Ele responde ao desafio "Fragmentação do Tratamento de Denúncias Recebidas via Conecta Recife", do Banco de Oportunidades da Prefeitura do Recife.

O produto é um painel analítico para **gestores públicos**. A pergunta que ele responde: onde, em quais serviços e em que etapa entre o canal e o órgão as demandas se repetem, demoram ou ficam sem resposta. A base tem 2,64 milhões de registros de cinco fontes públicas (156/Emlurb, Defesa Civil, Ouvidoria, SEDEC e Câmara Municipal), de 2012 a 2026, só do Recife.

## Onde está cada coisa

| Preciso de... | Abra |
|---|---|
| Problema, equipe, prazos, entregas, achados da EDA | [docs/contexto.md](docs/contexto.md) |
| Containers, fluxo de dados, rotas, telas | [docs/arquitetura.md](docs/arquitetura.md) |
| Camadas e pastas dentro de cada container (Clean Architecture) | [docs/clean-architecture.md](docs/clean-architecture.md) |
| Tecnologias, versões e o que está decidido ou só proposto | [docs/stack.md](docs/stack.md) |
| Clean Code, comentários, travessão, convenções de Python, TypeScript, SQL e API | [docs/padroes-de-codigo.md](docs/padroes-de-codigo.md) |
| Cores, tipografia, gráficos, mapas e tom do texto | [docs/design-system.md](docs/design-system.md) |
| Dataset, fontes, privacidade e armadilhas dos dados | [docs/dados.md](docs/dados.md) |
| Decisões técnicas, aceitas e em aberto | [docs/adr/README.md](docs/adr/README.md) |
| Branches, commits, PRs e definição de pronto | [CONTRIBUTING.md](CONTRIBUTING.md) |
| O que é cada documento, skill, agente e hook do projeto | [MAPA-DO-REPOSITORIO.md](MAPA-DO-REPOSITORIO.md) |
| Como rodar cada parte | [README.md](README.md) e o README de `frontend/`, `backend/` e `processor/` |

O histórico completo do grupo (entregas semanais, relatórios, dataset) fica no Google Drive. O repositório é **público**, então o link da pasta não entra em nenhum arquivo versionado: ele é compartilhado só entre o grupo. O mesmo vale para números de protocolo, e-mails e qualquer detalhe que aponte para dado pessoal.

## Stack definida pelo grupo

| Camada | Tecnologia |
|---|---|
| Frontend | SPA em React, Recharts para gráficos, Leaflet para o mapa coroplético |
| Backend | API REST em Python com FastAPI |
| Banco | PostgreSQL |
| Processor | Script Python agendado (cron) por regras do AWS EventBridge, que ingere e transforma os dados da Prefeitura periodicamente |

As ferramentas complementares (TypeScript, Vite, uv, Ruff, Alembic etc.) estão em [docs/stack.md](docs/stack.md), cada uma com status. **Proposta não é decisão:** não use uma ferramenta marcada como "proposta" sem o grupo confirmar.

## Regras que não se negociam

1. **Privacidade dos dados.**
   - O texto da SEDEC (coluna `texto` das linhas `SEDEC_CHAMADOS`) nunca sai do grupo. Ele não aparece em resposta de API, fixture, log, print de tela, issue nem commit. O mascaramento dele é heurístico.
   - O sal do `id_local` (`.salt_id_local`) e qualquer outro segredo nunca entram no repositório. Segredo vem de variável de ambiente ou de gerenciador de segredos.
   - Arquivos de dados (CSV, XZ, ZIP, Parquet, dumps) não entram no git. Eles ficam no Drive (ver [docs/dados.md](docs/dados.md)).
   - Se encontrar dado pessoal em claro em qualquer lugar, pare e avise. Não copie o registro.
2. **Nada se apaga sem autorização.** No Drive, quem apaga é o Gustavo. Arquivo já entregue no Classroom não se edita. No repositório, remover arquivo exige motivo no commit.
3. **Decisões de engenharia são do grupo.** É orientação do Prof. Marcelo. Seu papel é apresentar opções com prós e contras e registrar uma ADR com status "proposta". Não implemente uma decisão em aberto como se estivesse tomada. A lista das que estão em aberto fica em [docs/adr/README.md](docs/adr/README.md).
4. **Nenhum número inventado.** Todo número em tela, documento ou commit sai de uma consulta reproduzível e informa fonte, período e filtro. A reincidência tem três definições em circulação (38,6%, 36,3% e 53,3%), então diga sempre qual delas está usando.
5. **Os mockups do Drive são conceituais.** Sirvam de referência de layout; os números deles são fictícios e não devem ser copiados.

## Como trabalhar aqui

**Antes de mudar**
- Leia o documento da área e o README da pasta em que vai mexer.
- Para mudança grande (nova tela, nova rota, novo adaptador de fonte, mudança de esquema), descreva o plano antes de escrever código.

**Enquanto muda**
- Para qualquer código, use a skill `codigo-limpo`: ela confere a camada, a regra da dependência, os nomes, os comentários e o travessão.
- Para qualquer coisa visual (tela, componente, gráfico, mapa, texto de interface), use a skill `interface-recifeview` e [docs/design-system.md](docs/design-system.md).

**Antes de dar como pronto** (definição de pronto completa em [CONTRIBUTING.md](CONTRIBUTING.md#definição-de-pronto))
- Lint, formatação e testes passam na parte alterada.
- A documentação foi atualizada junto com a mudança. Se você instalou ou removeu dependência, criou variável de ambiente, comando, porta, pasta ou rota, use a skill `atualizar-docs`. Um README que não ensina a rodar o projeto do zero é considerado bug.
- Se você criou, renomeou ou removeu um `.md`, uma skill, um agente ou um hook, o [MAPA-DO-REPOSITORIO.md](MAPA-DO-REPOSITORIO.md) foi atualizado no mesmo commit. O hook `Stop` em `.claude/settings.json` confere isso e devolve a tarefa se algo ficar de fora.
- Commit feito com a skill `commit`.

## Commits

Resumo; a regra completa está em [CONTRIBUTING.md](CONTRIBUTING.md#commits).

```
tipo(escopo): descrição no imperativo, em minúsculas, sem ponto final
```

Exemplo: `feat(frontend): adiciona filtro de período ao mapa de bairros`

- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Escopos: `frontend`, `backend`, `processor`, `db`, `infra`, `adr`, `repo`. Documentação geral vai sem escopo (`docs: ...`).
- Um assunto por commit. Dependência nova vai num commit `build` separado da funcionalidade que a usa, e formatação nunca entra junto com mudança de comportamento.
- Trabalhe numa branch (`tipo/descricao-curta`), nunca direto na `main`. Nunca use `--no-verify` nem force push na `main`.
- Ao concluir uma unidade de trabalho, faça o commit: o grupo quer um histórico contínuo e legível.

## Código limpo

Decisão registrada na [ADR 0003](docs/adr/0003-clean-architecture-e-clean-code.md).

**Clean Architecture** ([docs/clean-architecture.md](docs/clean-architecture.md))
- Quatro camadas em cada container: `domain`, `application` (casos de uso e portas), `infrastructure` e entrada (routers, handler, páginas).
- As dependências só apontam para dentro. O domínio não conhece framework, banco nem rede. Só o ponto de montagem conhece as implementações concretas.
- Decisão em aberto vira porta com implementação local. A versão de nuvem não é escolhida por conta própria.

**Clean Code** ([docs/padroes-de-codigo.md](docs/padroes-de-codigo.md#clean-code))
- Nomes que dizem o que a coisa é. Funções curtas, que fazem uma coisa, com até 3 parâmetros e sem flag booleana.
- Guarda e retorno antecipado, sem número nem string mágica, exceção com nome do domínio.
- Sem código morto, sem `print` esquecido, sem abstração antes da terceira repetição.

**Comentários:** só quando forem indispensáveis para entender o porquê e o código não conseguir dizer isso sozinho. Antes de comentar, renomeie, extraia função ou constante, ou escreva um teste.

**Travessão:** nada que faça parte da aplicação usa travessão (—) nem meia-risca (–). Isso vale para texto de interface, strings, mensagens de erro, logs, comentários, commits e documentação. Use vírgula, dois-pontos, parênteses ou "a" em intervalos (`2021 a 2025`).

## Idioma

- Documentação, commits, comentários e textos de interface: português do Brasil.
- Código: conceitos e ações do domínio em português, sem acento e iguais ao [dicionário de colunas](docs/dados.md#colunas-principais) (`bairro_oficial`, `listar_prazos_por_servico`). Papéis técnicos em inglês (`PrazoRepository`, `domain/`, `routers/`, `useFiltrosGlobais`).

## Nada com cara de gerado por IA

Isso vale para a interface, a documentação e os commits. O detalhe está em [docs/design-system.md](docs/design-system.md#o-que-evitar).

- Use a identidade do RecifeView: fundo branco predominante, texto preto, destaques em `#0F62FE`, apoio em `#EAF2FF`, Montserrat.
- Não use emoji, travessão, gradientes roxos, glassmorphism, ícone decorativo em todo título, frase de efeito ("Insights poderosos"), boas-vindas genéricas nem dado de exemplo apresentado como se fosse real.
- O texto deve ser direto e específico do Recife e dos dados. Cada gráfico informa fonte, período e o que mostra.

## Estado atual (26/10/2026)

- Repositório público no GitHub: https://github.com/Mateus-Ribeir0/RecifeView, branch principal `main`.
- O repositório tem só documentação e estrutura de pastas. Ainda não há código.
- A próxima entrega é a da Semana 13, em 30/10. Pela ordem da lista de AVD, deve ser a N4 (Dashboard Interativo, versão inicial). Confirme o enunciado no Classroom.
- Se o git de uma máquina não tiver nome e e-mail configurados, os commits falham. Nesse caso, avise em vez de configurar uma identidade por conta própria.

Atualize esta seção sempre que o estado mudar.
