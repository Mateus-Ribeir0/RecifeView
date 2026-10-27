# Registro de decisões (ADR)

Cada decisão técnica que muda a forma do sistema ganha um arquivo curto aqui: o contexto, a decisão e as consequências. Isso alimenta a Documentação Final (N9), que pede o histórico de decisões, e treina o que o Prof. Marcelo quer exercitar: decidir pensando em escala, custo e crescimento.

## Quando escrever uma ADR

- Escolher, trocar ou remover uma tecnologia.
- Decidir onde algo roda ou onde algo é guardado.
- Mudar um contrato entre containers (formato da API, esquema do banco).
- Definir uma métrica que aparece no painel.

## Como escrever

1. Copie [0000-modelo.md](0000-modelo.md) para `NNNN-titulo-em-kebab-case.md`, com o próximo número livre.
2. Comece com o status **proposta**.
3. Leve para o grupo (ou para o Prof. Marcelo, se for decisão de arquitetura). Quando houver acordo, mude para **aceita** e registre a data e quem decidiu.
4. ADR aceita não se edita. Se a decisão mudar, escreva uma nova ADR que a **substitui** e marque a antiga como **substituída por NNNN**.
5. Commit: `docs(adr): registra decisão sobre ...`.

## Índice

| Nº | Decisão | Status | Data |
|---|---|---|---|
| [0001](0001-stack-do-projeto.md) | Stack do projeto | Aceita | 26/10/2026 |
| [0002](0002-leaflet-para-mapa-coropletico.md) | Leaflet para o mapa coroplético | Aceita | 26/10/2026 |
| [0003](0003-clean-architecture-e-clean-code.md) | Clean Architecture e Clean Code | Aceita | 26/10/2026 |
| [0004](0004-ferramentas-complementares.md) | Ferramentas complementares de frontend, backend e ambiente local | Aceita | 26/10/2026 |
| [0005](0005-autenticacao-com-jwt-proprio.md) | Autenticação com JWT próprio atrás de uma porta | Proposta | 26/10/2026 |

## Decisões em aberto

Levantadas ao montar o C4 v0.1 (15/10/2026) e ao definir a stack. Cada uma vira uma ADR quando for decidida.

| Decisão | Opções na mesa | O que pesa |
|---|---|---|
| Onde guardar a camada bruta | Amazon S3 ou schema `raw` no PostgreSQL | A N2 exige separar bruto e tratado. O S3 é barato para arquivo grande; no schema `raw` fica tudo num lugar só |
| Onde roda o Processor | AWS Lambda ou ECS/Fargate | O Lambda tem limite de 15 minutos, e a carga histórica tem cerca de 2,6 milhões de linhas. Dá para combinar: Fargate na carga completa e Lambda no incremental |
| Autenticação | JWT próprio ou serviço gerenciado (ex.: Amazon Cognito) | Já existe uma implementação local com JWT próprio atrás de portas, descrita na [ADR 0005](0005-autenticacao-com-jwt-proprio.md) (proposta). Falta o grupo aceitar ou trocar pelo serviço gerenciado |
| Seta sem destino abaixo da API no esboço | Cache, fila, módulo de ML ou outro serviço | Perguntar ao Prof. Marcelo |
| Ferramentas ainda propostas | TanStack Query, react-leaflet, GitHub Actions, pre-commit com commitlint | Confirmar quando forem necessárias (ver [stack.md](../stack.md)) |
| Definição de reincidência | Uma das três em [dados.md](../dados.md#definições-de-métricas) | Precisa estar fechada antes da tela de Recorrências |
| Índice de prioridade (AHP) | Por registro, por bairro ou ambos; mapa de pontos ou por bairro | Perguntar à Profª Maíra e ao Prof. Marcelo o que esperam |
