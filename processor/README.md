# Processor

Job em Python que coleta os dados públicos da Prefeitura e das outras fontes, limpa, pseudonimiza, unifica no esquema comum e carrega no PostgreSQL. É disparado por uma regra agendada do AWS EventBridge.

É a versão de produção do pipeline que já existe no Drive (`Dados/02_fontes_separadas/scripts/pipeline.py` e `Dados/01_DATASET_PRINCIPAL_recifeview-dataset/build_dataset.py`). As contagens desses scripts já foram conferidas contra a base unificada da Semana 10, então reaproveite a lógica deles e confira se o resultado continua batendo.

> Ainda não há código nesta pasta. Ao criar o projeto, preencha as seções marcadas com "a preencher" no mesmo commit.

## Etapas

| Etapa | O que faz |
|---|---|
| Ponto de entrada | Recebe o evento (fonte e modo: incremental ou carga completa) e orquestra |
| Extratores | Um adaptador por fonte: Dados Abertos, Câmara (SAGL), IBGE/SIDRA, catálogo do Conecta, SEDEC (arquivo de 03/2024, carga única) |
| Limpeza e normalização | Grafias, datas, mudanças de esquema, 94 bairros oficiais, correções da N3 |
| Pseudonimização | `id_local` com sal, coordenadas com 3 casas, mascaramento do texto SEDEC |
| Unificador | Esquema comum das 5 fontes |
| Carregador | Upsert idempotente: rodar de novo não duplica |
| Qualidade | Registro de cada execução com contagens de entrada, descarte e saída |

Detalhes em [docs/arquitetura.md](../docs/arquitetura.md#processor) e nos cuidados de [docs/dados.md](../docs/dados.md#cuidados-antes-de-usar).

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `entrypoints`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#processor). As regras de limpeza, normalização e pseudonimização são funções do domínio sobre `DataFrame`. Coleta, armazenamento, carga e segredos são adaptadores atrás de portas.

## Decisões em aberto que afetam esta pasta

- Onde guardar a camada bruta: S3 ou schema `raw`. Na prática, isso define qual adaptador implementa a porta `ArmazenamentoBruto`.
- Onde rodar: Lambda (limite de 15 minutos) ou ECS/Fargate. Isso muda só `entrypoints/`.

Ver [docs/adr/README.md](../docs/adr/README.md#decisões-em-aberto). Até a decisão, implemente só a versão local (sistema de arquivos e variável de ambiente).

## Segredos

O sal do `id_local` vem do gerenciador de segredos em produção e de variável de ambiente local. Ele nunca é commitado, nunca aparece em log e nunca vai para o banco.

## Pré-requisitos

A preencher: versão do Python e gerenciador de dependências.

## Como rodar localmente

A preencher:

1. Instalar as dependências.
2. Copiar `.env.example` para `.env` e configurar o sal e a conexão com o banco.
3. Rodar a carga completa de uma fonte.
4. Rodar a carga incremental.
5. Conferir o relatório de qualidade.

## Variáveis de ambiente

| Variável | Para quê | Exemplo |
|---|---|---|
| A preencher | | |

## Comandos

| Comando | O que faz |
|---|---|
| A preencher | Carga completa, incremental, lint, formatação, testes |

## Agendamento

A preencher quando a infraestrutura existir: expressão da regra do EventBridge (cron ou rate), por fonte, e como disparar manualmente.
