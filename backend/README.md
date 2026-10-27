# Backend

API REST do RecifeView. Ela autentica o gestor, aplica as permissões, registra a auditoria das consultas e devolve os indicadores já calculados (agregações, percentis, per capita, reincidência e priorização) para o frontend.

**Stack:** Python e FastAPI, com PostgreSQL. As ferramentas complementares estão em [docs/stack.md](../docs/stack.md#backend).

> Ainda não há código nesta pasta. Ao criar o projeto, preencha as seções marcadas com "a preencher" no mesmo commit.

## Rotas previstas

Um router por tela do painel, todas sob `/api/v1`:

| Router | Responde |
|---|---|
| Autenticação | Login, emissão e renovação de token |
| Indicadores | KPIs da Visão Geral |
| Território | Demanda por bairro e RPA, per capita, prioridade |
| Prazos | Mediana, p90 e estoque aberto por serviço e órgão |
| Recorrências | Duplicidade e reincidência |
| Fluxo Câmara → Prefeitura | Envio, canal e resposta das indicações |
| Catálogos e filtros | Serviços, bairros e órgãos |
| Modelos (bônus) | Demanda esperada e classificador |

Convenções de rota, filtros e formato de resposta em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#api-rest).

## Estrutura

Camadas `domain`, `application`, `infrastructure` e `api`, conforme [docs/clean-architecture.md](../docs/clean-architecture.md#backend-fastapi). O router valida e chama um caso de uso; o caso de uso aplica as regras do domínio e usa portas; os repositórios SQLAlchemy implementam as portas. O cálculo pesado roda no banco, mas a regra é definida no domínio.

## Regra de privacidade

Nenhuma rota devolve o texto da SEDEC. Os schemas de resposta são explícitos justamente para que uma coluna nova no banco não vaze por acidente. Ver [docs/dados.md](../docs/dados.md#privacidade-lgpd).

## Pré-requisitos

A preencher: versão do Python (`.python-version`), gerenciador de dependências e PostgreSQL local.

## Como rodar

A preencher:

1. Subir o PostgreSQL local.
2. Instalar as dependências.
3. Copiar `.env.example` para `.env` e ajustar.
4. Aplicar as migrações.
5. Subir a API (indicar porta e o endereço da documentação OpenAPI).

## Variáveis de ambiente

| Variável | Para quê | Exemplo |
|---|---|---|
| A preencher | | |

## Comandos

| Comando | O que faz |
|---|---|
| A preencher | Rodar, migrar, lint, formatação, tipos, testes |

## Banco de dados

As migrações ficam nesta pasta, para que o esquema tenha um dono só (proposta; ver [docs/arquitetura.md](../docs/arquitetura.md#organização-do-repositório)). Convenções de nomes e schemas em [docs/padroes-de-codigo.md](../docs/padroes-de-codigo.md#banco-de-dados-postgresql).
