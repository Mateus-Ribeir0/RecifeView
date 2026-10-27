# 0003. Organizar o código em camadas (Clean Architecture) e seguir Clean Code

- **Status:** aceita
- **Data:** 26/10/2026
- **Quem decidiu:** grupo

## Contexto

São três containers (frontend, backend, processor) escritos por sete pessoas em cerca de sete semanas, com avaliação técnica de peso 6 no SR2. Três decisões de infraestrutura continuam em aberto (onde guardar o dado bruto, onde roda o Processor, como autenticar), e o código precisa avançar antes delas. As regras centrais do projeto (percentil, reincidência, per capita, pseudonimização, o bloqueio do texto da SEDEC) precisam ser testáveis e não podem depender de detalhe de framework.

O C3 v0.1 já separa routers, serviços e repositórios na API, mas não diz para que lado as dependências apontam.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Camadas técnicas simples (routers, services, repositories) | Pouco código, todo mundo conhece | O serviço acaba importando SQLAlchemy e boto3; trocar S3 por `raw` ou Lambda por Fargate espalha mudança; teste de regra exige banco |
| Clean Architecture pragmática (domínio, aplicação com portas, infraestrutura, entrada) | Regras testáveis sem entrada nem saída; decisões em aberto viram adaptadores; fronteira clara para a privacidade | Mais arquivos e disciplina de importação |
| Clean Architecture completa com DDD tático, CQRS e eventos de domínio | Máximo isolamento | Cerimônia demais para o prazo e para o tamanho do sistema |

## Decisão

Clean Architecture pragmática nos três containers, conforme [clean-architecture.md](../clean-architecture.md), com duas exceções conscientes: o pandas é permitido no domínio do Processor (desempenho com 2,6 milhões de linhas), e o cálculo pesado roda no banco, com a regra definida no domínio e executada pelo repositório.

Junto com isso, o grupo adota as práticas de Clean Code de [padroes-de-codigo.md](../padroes-de-codigo.md): nomes que dispensam comentário, funções pequenas, comentário só quando indispensável e nenhum travessão em nada que faça parte da aplicação.

## Consequências

- Os componentes do C3 continuam valendo e se encaixam nas camadas (tabela em [clean-architecture.md](../clean-architecture.md#backend-fastapi)). O `.drawio` pode ganhar a indicação de camada numa próxima revisão.
- Enquanto as decisões de infraestrutura estiverem em aberto, só a implementação local das portas é feita.
- A revisão de PR passa a checar a regra da dependência. A checagem automática (`import-linter`, `eslint-plugin-boundaries`) fica como proposta em [stack.md](../stack.md).
- A Documentação Final (N9) ganha um argumento técnico explícito para a organização do código.
