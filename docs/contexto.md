# Contexto do projeto

Retrato de 26/10/2026, feito a partir da pasta `Contexto` do Drive (atualizada em 19/10) e da entrega N3 (23/10). Quando algo aqui divergir do Drive ou do Classroom, eles valem mais. Atualize este arquivo quando houver entrega nova ou decisão nova.

## Links

| O quê | Onde |
|---|---|
| Pasta do grupo no Drive (P5G8) | Link compartilhado só entre o grupo, no Slack. Ele não entra aqui porque o repositório é público e a pasta guarda o dataset com o texto da SEDEC |
| Resumos de contexto (comece pelo `LEIA-PRIMEIRO.md`) | Drive › `Contexto` |
| Entregas semanais | Drive › `Entregaveis` |
| Dataset e scripts do pipeline | Drive › `Dados` |
| Diagramas C4 (`.drawio` e PNGs) | Drive › `Arquitetura C4 - RecifeView` |
| Marca, banners e mockups | Drive › `AssetsVisuais` |
| Google Site do projeto | https://sites.google.com/cesar.school/recifeview/início |
| Desafio da Prefeitura | https://inovacaoaberta.recife.pe.gov.br/ |

## O problema

O desafio é "Fragmentação do Tratamento de Denúncias Recebidas via Conecta Recife", do Banco de Oportunidades da Prefeitura do Recife.

O cidadão já tem bons canais de entrada. A dificuldade está do lado de dentro da Prefeitura: consolidar registros de áreas diferentes, perceber que dois registros falam do mesmo problema, priorizar, encaminhar ao órgão certo e transformar o histórico em informação para a gestão. As bases públicas (156/Emlurb, Ouvidoria, Defesa Civil, SEDEC, Câmara) não têm chave em comum, e o cruzamento só é possível por bairro, serviço e período.

**Usuário do produto:** o gestor público. O RecifeView não faz triagem do lado do cidadão. Ele é análise e visualização para quem decide. É isso que o diferencia das três soluções já submetidas por terceiros ao mesmo desafio.

**Pergunta central (N1):** onde, em quais serviços e em que etapa do caminho entre canal e órgão as demandas se repetem, demoram ou ficam sem resposta, e como mostrar isso à gestão?

**Escopo:** município do Recife e órgãos da Prefeitura. Dados de outras cidades não entram, nem para treino.

## Disciplina e equipe

- Projetos 5, CESAR School, 2026.2. Grupo 08, formado só por alunos de Ciência da Computação, na trilha de Análise e Visualização de Dados (AVD), 5º período.
- Orientador: Prof. Marcelo Arcoverde. Atendimento fixo às terças, 14h, com presença obrigatória.
- Professora da trilha de AVD: Profª Maíra Farias.
- Canal do grupo no Slack: `#grupo08-projetos5-2026-2`.
- Integrantes: Davi Santiago, Gustavo Henrique Cruz de Oliveira, Henrique Sérgio C. de Brito, João Pedro R. Dornelas de Araujo, Lucas Ramon, Lucas Rodrigues Campos e Mateus de Almeida Ribeiro.

## Cronograma

Entrega não feita na semana prevista vale zero, mesmo se enviada depois.

| Semana | Data | Entrega | Situação |
|---|---|---|---|
| 10 | 09/10 | N1 Plano de Análise de Dados | Entregue |
| 11 | 16/10 | N2 Plano de Preparação de Dados | Entregue |
| 12 | 23/10 | N3 Análise Exploratória de Dados (EDA) | Entregue |
| 13 | 30/10 | Provavelmente N4 Dashboard Interativo, versão inicial | Confirmar enunciado no Classroom |
| 14 | 06/11 | Ciclo de desenvolvimento | Confirmar enunciado |
| 15 | 13/11 | Ciclo de desenvolvimento | Confirmar enunciado |
| 16 | 20/11 | Ciclo de desenvolvimento | Confirmar enunciado |
| 17 | 27/11 | Ciclo de desenvolvimento | Confirmar enunciado |
| 18 | 04/12 | Preparação do SR2 | |
| 19 | 11/12 | SR2, apresentação final (último dia de aula) | |

Fonte das datas, em ordem de prioridade: anúncio do orientador no Slack com data e hora, depois o Calendário Acadêmico 2026.2, depois a apresentação "Projeto (5e6) - 2026.2" e por último o Manual do Estudante.

## Entregáveis de AVD

Lista revisada do Classroom: nove itens obrigatórios e um bônus. O Classroom não diz em que semana cai cada item depois da N2.

| Nº | Entregável | O que pede | Onde o código ajuda |
|---|---|---|---|
| 1 | Plano de Análise de Dados | Problema, hipóteses, fontes, visualizações previstas | Entregue |
| 2 | Plano de Preparação de Dados | Fontes validadas, limpeza, pipeline bruto e tratado | Entregue |
| 3 | EDA | Notebook com os quatro princípios, interpretação de cada gráfico, outliers | Entregue |
| 4 | Dashboard Interativo, versão inicial | Primeira versão funcional, pelo menos um filtro, narrativa visual coerente | `frontend/` e `backend/` |
| 5 | Proposta de Integração e Publicação | Estrutura das páginas e ferramenta de publicação | [arquitetura.md](arquitetura.md) |
| 6 | Dashboard Consolidado | Ponta a ponta, com dados carregados e documentação das decisões visuais | Todos os containers |
| 7 | Versão Quase Final | Ajustes após testes de uso, dizendo o que foi validado | Todos |
| 8 | Storytelling e Pitch | Peça narrativa visual com pré-atenção e Gestalt | [design-system.md](design-system.md) |
| 9 | Documentação Final | Histórico de decisões, capturas, síntese de insights | [adr/](adr/README.md) e tags de entrega |
| Bônus | Modelagem preditiva | Regressão ou classificação, com métricas e interpretação | Rota "Modelos" da API |

A N5 pede a escolha da ferramenta de publicação. Os documentos antigos (Proposição de Projeto e N1) falavam em "Streamlit ou Power BI". A stack atual responde isso: SPA própria em React, com o Streamlit servindo no máximo como protótipo.

## Notas e regras da disciplina

- O grupo segue o Modelo B (100% CC). Nota do grupo no SR2 = (Processo × 4 + Técnica × 6) / 10. A nota do grupo é o teto da nota individual.
- Para passar de fase (Descoberta, Prova de Conceito, Protótipo com Aplicação Real) é preciso a validação dos orientadores em cada Status Report.
- A declaração de uso de IA é preenchida toda semana. As entregas trazem a nota "Esta entrega foi auxiliada por IA; o grupo revisou o conteúdo".
- O FACT é liberado 72h antes do SR1/SR2. Quem não enviar até o horário-limite tira zero.

## O que a EDA (N3) encontrou

Esses resultados orientam o que o painel precisa mostrar. Os números vêm da N3; recalcule antes de exibir.

| Hipótese | Resultado | Implicação para o painel |
|---|---|---|
| H1 Fragmentação do destino | Confirmada, varia por tipo. Manutenção vai ~90% para a Emlurb; pavimentação, escadaria, praças e risco se espalham (o órgão principal fica com 38% a 75%). | Fluxo (Sankey) das categorias que mudam de mão |
| H2 Retorno raro e lento | Confirmada. 97% das indicações da Câmara chegam à Prefeitura, só 21% têm resposta registrada, em mediana 241 dias depois. | Funil Câmara → Prefeitura |
| H3 Reincidência | Confirmada e refinada. 53% dos pedidos do 156 com endereço completo caem num local + serviço repetido; 64% das repetições ocorrem 30 dias ou mais depois; só 19% são duplicidade de até 7 dias. | Separar duplicidade de reincidência |
| H4 Prazos piorando | Confirmada na cauda. Mediana entre 3 e 7 dias; p90 sobe de 29 a 52 dias (2015 a 2020) para 55 a 87 dias (2021 a 2024). | Mostrar percentis, não média |
| H5 Backlog em área de risco | Mantida. SEDEC com 88,6% "em tramitação" na cópia de 03/2024. | Avisar que a situação está congelada |
| H6 Subnotificação territorial | Reformulada. A vulnerabilidade não reduz o uso do 156 por habitante (ρ = −0,13, não significativo), mas se associa à demanda de emergência (Defesa Civil, ρ = 0,37). | Dois mapas de prioridade: serviço urbano e emergência apontam para bairros diferentes |
| H7 Chuva e demanda | Estudo futuro. Só a sazonalidade foi descrita (pico em julho e agosto). | Fora do escopo atual |
| H8 Catálogos não conversam | Não testada. | |
| H9 Canal digital e retorno | Indício forte. A resposta registrada sai de 0,7% (2022) para 44,8% (2025) com o envio por sistema. | Série de canal de envio × resposta |

O K-Means da N3 gerou 4 perfis de bairro (silhueta ≈ 0,27). O perfil de risco forma um arco na periferia (Norte, Noroeste, Várzea e Sul).

Para o dashboard, a N3 recomenda: o fluxo das categorias que mudam de mão, os pontos crônicos de reincidência, o prazo por categoria e percentil e dois mapas de prioridade.

## Pendências que afetam o código

| Pendência | Situação em 26/10 | Efeito no código |
|---|---|---|
| Pedido LAI ao SGDE (protocolado em 08/10; número no Drive) | Prazo 28/10, prorrogável até 07/11 | Se chegar, vira um novo adaptador no Processor e permite medir a fragmentação pedido a pedido |
| Entrevista e amostra de dados da Emprel | Não aconteceu | Nenhum, por enquanto |
| Levar as correções da N3 para o pipeline (órgãos da Ouvidoria, grafias do 156, bairro da Câmara pela ementa, anulações) | Feito só no notebook | Precisa entrar no Processor |
| Padronizar a definição de reincidência | Em aberto | Ver [dados.md](dados.md#definições-de-métricas) |
| Priorização com AHP e mapa de prioridade (sugestão da Profª Maíra, 19/10) | Perguntar à Maíra e ao Marcelo o formato esperado | Índice calculado no backend ou no Processor; mapa no frontend |
| Decisões de arquitetura em aberto | Ver [adr/README.md](adr/README.md) | Bloqueiam partes da infraestrutura |

## Identidade

- O nome RecifeView é definitivo e consta no documento oficial entregue.
- A identidade visual do RecifeView substitui a da CESAR nas entregas do grupo. Ver [design-system.md](design-system.md).
- Mockups e imagens de equipe da pasta `AssetsVisuais` são conceituais ou sintéticos. Não comprovam funcionalidade nem mostram pessoas reais.
