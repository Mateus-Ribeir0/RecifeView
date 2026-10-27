---
name: atualizar-docs
description: Mantém README, docs/ e .env.example do RecifeView em dia com o código. Use depois de instalar, remover ou atualizar dependência; criar variável de ambiente, comando, script, porta, pasta, rota da API, tabela ou migração; tomar uma decisão técnica; mudar uma métrica; ou quando pedirem "atualiza o README" ou "documenta isso". Também use antes de todo commit que mude a forma de rodar o projeto.
---

# Atualizar a documentação do RecifeView

Regra do grupo: qualquer integrante precisa conseguir clonar o repositório e rodar o projeto só lendo os READMEs. Um README desatualizado é bug.

## 1. Descubra o que mudou

```bash
git status
git diff
git diff --staged
```

## 2. Atualize o que a mudança afeta

| Se você... | Atualize |
|---|---|
| Instalou, removeu ou atualizou uma dependência | README da pasta (pré-requisitos, se for o caso) e a tabela de [docs/stack.md](../../../docs/stack.md) com status e motivo |
| Promoveu uma ferramenta de "Proposta" para uso | [docs/stack.md](../../../docs/stack.md) e uma ADR nova em [docs/adr/](../../../docs/adr/README.md) |
| Criou ou renomeou uma variável de ambiente | `.env.example` da pasta (valor falso e seguro) e a tabela "Variáveis de ambiente" do README da pasta |
| Criou um comando ou script (dev, build, teste, carga) | Tabela "Comandos" do README da pasta |
| Mudou porta, URL ou endereço da documentação da API | "Como rodar" do README da pasta e do README da raiz |
| Criou uma camada, uma porta nova ou mudou onde algo mora dentro de um container | [docs/clean-architecture.md](../../../docs/clean-architecture.md) |
| Criou uma pasta de primeiro nível ou um container | "Estrutura do repositório" no README da raiz, [docs/arquitetura.md](../../../docs/arquitetura.md) e o mapa do `CLAUDE.md` |
| Criou ou mudou uma rota da API | Tabela de rotas de `backend/README.md` e, se mudou a tela correspondente, [docs/arquitetura.md](../../../docs/arquitetura.md#telas-e-rotas-da-api) |
| Criou uma tabela, view ou migração | `backend/README.md` (seção "Banco de dados") se mudar como se prepara o banco |
| Criou uma tela | Tabela de telas de `frontend/README.md` e [docs/arquitetura.md](../../../docs/arquitetura.md#telas-e-rotas-da-api) |
| Adicionou ou alterou um adaptador de fonte | `processor/README.md` e, se a fonte for nova, [docs/dados.md](../../../docs/dados.md#fontes) |
| Mudou a definição de uma métrica | [docs/dados.md](../../../docs/dados.md#definições-de-métricas) e o texto da tela que a explica |
| Tomou uma decisão técnica | ADR nova e o índice de [docs/adr/README.md](../../../docs/adr/README.md), retirando o item de "Decisões em aberto" |
| Mudou o estado do projeto (entrega feita, remoto criado, primeiro código) | Seção "Estado atual" do `CLAUDE.md`, "Situação" do README da raiz e [docs/contexto.md](../../../docs/contexto.md) |
| Mudou cor, fonte ou componente base | [docs/design-system.md](../../../docs/design-system.md) |
| Criou, renomeou ou removeu um `.md`, uma skill, um agente ou um hook | [MAPA-DO-REPOSITORIO.md](../../../MAPA-DO-REPOSITORIO.md): a linha na tabela certa, com link e explicação de para quê serve e como contribui. Siga a seção "Como adicionar um item novo" de lá |

Quando uma seção "A preencher" puder ser preenchida, preencha e retire o aviso de que a pasta ainda não tem código.

## 3. Escreva do jeito do projeto

- Português do Brasil, frases diretas, sem emoji e sem travessão (— ou –). Em intervalos, use "a": `2021 a 2025`.
- Comandos em bloco de código, prontos para copiar, na ordem em que se executam.
- Diga a versão quando ela importar (Node, Python, PostgreSQL).
- Não documente o que o código já diz sozinho. Documente o que alguém precisa saber para rodar, configurar ou não quebrar.
- Datas em `dd/mm/aaaa`.

## 4. Confira

- Releia o "Como rodar" como alguém que acabou de clonar o repositório. Cada passo funciona na ordem? Falta algum pré-requisito?
- Os links entre documentos continuam apontando para títulos que existem?
- O `.env.example` tem todas as variáveis que o código lê?
- `bash .claude/hooks/conferir-mapa.sh` termina sem listar nada?

## 5. Commit

A documentação entra **no mesmo commit** da mudança que a motivou (use a skill `commit`). Só use um commit `docs` separado quando a mudança for apenas de documentação.
