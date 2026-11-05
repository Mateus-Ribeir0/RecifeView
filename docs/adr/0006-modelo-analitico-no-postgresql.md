# 0006. Guardar a base analítica numa tabela fato com views materializadas

- **Status:** proposta
- **Data:** 05/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi aprovada por Mateus Ribeiro para levar o painel do Streamlit para o produto

## Contexto

O painel precisa das 8 páginas do protótipo em Streamlit, com filtros que recalculam tudo, e precisa aceitar arquivos novos. O Streamlit lê tabelas agregadas prontas (Parquet), geradas fora do app a partir do dataset do grupo. Agregado pronto não recebe dado novo: reincidência e percentil não se somam, porque dependem da linha original.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Dataset inteiro no PostgreSQL, com views materializadas | Importação recalcula tudo de verdade; uma regra vale para base e arquivo novo; é o desenho de [arquitetura.md](../arquitetura.md#camadas-de-dados) | Cerca de 1 GB de banco; carga inicial de alguns minutos; o SQL precisa reproduzir o pipeline do Streamlit |
| Só as tabelas agregadas do Streamlit | Sobe em segundos, ocupa pouco | Importação nova não recalcula reincidência nem percentil; duas fontes de verdade |
| Consultas direto na tabela fato, sem view | Sem etapa de atualização | Agregar 2,6 milhões de linhas a cada filtro não é viável |

## Decisão

Guardar os registros em `ouro.fato_demanda`, com a dimensão `ouro.dim_bairro`, e uma view materializada para cada tabela do painel. É a única opção em que importar um arquivo muda os indicadores de forma correta.

- A tabela fato leva só as colunas que o painel usa. Não entram: texto da SEDEC, ementa, coordenadas, autoria, protocolo nem endereço.
- `id_local` fica no banco para medir reincidência e nunca sai por rota.
- A chave `chave_registro` identifica a linha entre arquivos e torna a carga idempotente. Ela é um hash dos campos que definem o registro em cada fonte, com a ordem de aparição para separar registros iguais.
- A data de referência do estoque vem da `data_do_retrato` de cada importação, em vez de ficar fixa em 07/10/2026.
- "Arquivos recentes" são os dois arquivos anuais mais novos de cada fonte, que reproduz 2025 e 2026 no 156 e 2024 e 2025 na Ouvidoria.

## Consequências

- O SQL das views é a definição executável das métricas. Mudou a métrica, muda a migração e o [dados.md](../dados.md#definições-de-métricas) no mesmo PR.
- As views são atualizadas depois de cada importação, com o painel no ar.
- As tabelas do Streamlit viram referência para conferir contagens, como o arquivo do Drive.
- Quando o Processor existir, ele escreve nas mesmas tabelas. A coluna `importacao_id` continua dizendo de onde veio cada linha.
