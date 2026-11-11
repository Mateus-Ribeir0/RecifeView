# Dados

Resumo do que o código precisa saber sobre o dataset. A fonte completa é o `README.md` e o `dicionario_de_colunas.csv` em Drive › `Dados/01_DATASET_PRINCIPAL_recifeview-dataset` (versão 1.0, 13/10/2026). Leia esses dois arquivos antes de escrever qualquer cálculo.

## Como obter os dados

Os dados **não ficam no repositório**: o `.gitignore` bloqueia CSV, XZ, ZIP, Parquet e a pasta `data/`.

1. Baixe `recifeview_demandas_recife_2012_2026.csv.xz` (27 MB) de Drive › `Dados/01_DATASET_PRINCIPAL_recifeview-dataset`.
2. Coloque o arquivo em `data/` na raiz do repositório. A pasta é ignorada pelo git.
3. Não descompacte à toa: o pandas lê o `.xz` direto. Descompactado, o CSV tem 694 MB.
4. Não edite os arquivos da pasta `Dados` do Drive. Trabalhe numa cópia.

Quando o Processor estiver pronto, ele passa a ser o caminho oficial para popular o banco. O arquivo do Drive vira apenas referência para conferir contagens.

## O dataset

2.643.481 linhas × 45 colunas, de 2012 a 2026, só do município do Recife. Cada linha é um registro de uma fonte.

| `fonte` | Linhas | Período | O que uma linha representa |
|---|---|---|---|
| `156_EMLURB` | 1.377.158 | 2012 a 2026 | Solicitação de serviço urbano à Central 156 / Emlurb |
| `DEFESA_CIVIL` | 886.263 | 2014 a 2024 | **Ação** da Defesa Civil (vistoria, lona, monitoramento). Não é pedido |
| `OUVIDORIA` | 222.855 | 2018 a 2025 | Manifestação à Ouvidoria-Geral |
| `SEDEC_CHAMADOS` | 90.659 | 2012 a 2024 | Chamado em área de risco, com texto do cidadão (mascarado) |
| `CAMARA_REQUERIMENTOS` | 66.546 | 2021 a 2025 | Indicação ou requerimento de vereador, com a tramitação |

Além do dataset, a base recebe a sexta fonte, `FORMULARIO_PUBLICO`: relatos do formulário público revisados pela gestão ([ADR 0009](adr/0009-formulario-publico-e-pente-fino.md), proposta). Uma linha é uma ocorrência, que pode somar vários relatos. Ela usa as categorias e os códigos de serviço da Central 156 e fica fora das métricas do 156.

Dados de apoio: IBGE Censo 2022 por bairro (94 bairros, 1.488.920 habitantes), malha de bairros e RPAs em GeoJSON e o catálogo de serviços do Conecta Recife (840 serviços).

Papel de cada fonte (N2): o **núcleo** é formado por 156/Emlurb, Ouvidoria e Câmara; o **complemento**, por SEDEC e Defesa Civil; o **apoio**, por IBGE, malha e catálogo.

## Fontes

| Fonte | Origem | Licença ou natureza |
|---|---|---|
| 156/Emlurb, Defesa Civil, Ouvidoria, malha de bairros | Portal de Dados Abertos do Recife (dados.recife.pe.gov.br), baixados em 07/10/2026 | ODbL |
| SEDEC Chamados | Cópia de 09/03/2024 no Internet Archive (o dataset foi retirado do portal) | Dado público arquivado |
| Câmara Municipal | Sistema público SAGL (publico.recife.pe.leg.br), coletado em 07 e 08/10/2026 | Dado público |
| IBGE | Censo 2022, tabelas 9922, 9923 e 10206 | Dado público |
| Formulário público | Enviado por quem mora no Recife, sem identificação | Relato em quarentena até a revisão. Endereço e texto apagados em 90 dias |

A ODbL exige atribuição. O rodapé do painel cita as fontes.

## Colunas principais

A lista completa, com tipo e as fontes em que cada coluna é preenchida, está no `dicionario_de_colunas.csv`. Os nomes do código seguem esse dicionário.

| Grupo | Colunas |
|---|---|
| Comuns | `id`, `fonte`, `ano`, `mes`, `data_abertura`, `categoria`, `tipo_registro`, `orgao`, `situacao`, `iniciativa` |
| Prazo | `data_ult_movimento`, `dias_ate_movimento`; na Câmara, `camara_dias_ate_envio` e `camara_dias_ate_resposta` |
| Território | `bairro_oficial` (use este em mapas), `rpa`, `rpa_inferida`, `lat`, `lon`, `bairro_populacao_2022`, `bairro_pct_pop_favela_2022` |
| Reincidência | `id_local` (pseudônimo do endereço, vale só dentro da mesma fonte), `numero_informado` |
| Serviço | `servico_codigo`, `servico` |
| Canal e retorno | `canal_entrada`, `camara_canal_envio`, `camara_desfecho`, `ouv_no_prazo` |
| Texto | `texto` (SEDEC e Câmara), `rotulos_ocorrencia` |
| Consulta pelo cidadão | `protocolo`: o protocolo que a fonte publica (hoje, só o arquivo da Ouvidoria traz). Não existe no dataset do Drive; entra quando o arquivo da fonte é importado pelo painel ([ADR 0011](adr/0011-encaminhamento-ao-orgao-e-retorno.md)) |

## Privacidade (LGPD)

O que já foi feito no pipeline:

- Removidos: nome, CPF, telefone, e-mail, logradouro e número.
- O endereço virou `id_local`, um SHA-256 com sal secreto. O sal não fica no Drive nem no repositório.
- As coordenadas foram arredondadas para 3 casas decimais (cerca de 100 m).
- O texto da SEDEC passou por um mascaramento heurístico (`[N]`, `[NOME]`, `[EMAIL]`, `[LOCAL]`), que **não é garantido**.

Regras para o código:

| Regra | Por quê |
|---|---|
| O `texto` das linhas `SEDEC_CHAMADOS` nunca sai do banco: nem em API, log, fixture, print ou commit | O mascaramento pode ter falhado em algum registro |
| O `texto` da Câmara (ementa oficial) pode ser exibido | É publicação oficial |
| `id_local` não é exibido junto com coordenada | A combinação ajuda a reidentificar o endereço |
| O sal só existe no gerenciador de segredos ou no `.env` local | Com o sal, o hash pode ser revertido por força bruta sobre a lista de endereços |
| Classificação por texto (bônus) roda no backend ou no Processor; só o rótulo previsto sai | Pela mesma razão do texto SEDEC |
| Conta de cidadão vê de um relato só a rua da lista oficial e a faixa de numeração de 100 em 100; nunca o número, o texto nem quem relatou. O relato completo só volta para quem o enviou, em "Meus relatos" | O endereço pode ser o de quem relatou ([ADR 0010](adr/0010-contas-de-cidadao-e-niveis-de-acesso.md)) |
| O relato enviado com a conta aberta guarda o id da conta (`contribuicao.usuario_id`). Nenhuma tela, rota ou pacote da gestão lê esse campo | A gestão revisa sem saber quem relatou ([ADR 0010](adr/0010-contas-de-cidadao-e-niveis-de-acesso.md)) |
| Contas de cidadão guardam nome, e-mail e, se a pessoa quiser, o bairro. Nada de CPF ou telefone. Excluir a conta apaga esses dados | Minimização da LGPD |
| O `protocolo` só volta numa busca exata, pela página pública ou por "Meus pedidos". Nenhuma rota lista protocolos, e ele não vai para log nem para fixture com número real | É o identificador do pedido de alguém ([ADR 0011](adr/0011-encaminhamento-ao-orgao-e-retorno.md)) |
| Endereço e detalhe do formulário ficam só em `app.contribuicao`, nunca em `ouro.*`, no pacote, em log ou em rota pública, e são apagados em 90 dias | O texto é livre e o endereço pode ser o de quem relatou |

Algumas bases publicadas trazem dado pessoal exposto por defeito da própria fonte. Os detalhes ficam no Drive do grupo, fora deste repositório público, até a Prefeitura ser avisada. Esses registros nunca devem ser reproduzidos. Se o Processor encontrar algo parecido, ele descarta a linha e registra só a contagem.

## Cuidados antes de usar

Versão completa no README do dataset. Estes são os que mais afetam o código:

1. **Não há chave comum entre as fontes.** O cruzamento é por bairro, serviço e período, nunca por join de registro.
2. **Defesa Civil conta ações, não pedidos.** Separe por `iniciativa`: `CIDADAO` é demanda e `PROATIVA` é monitoramento. O grau de risco mudou de codificação entre 2016 e 2017. O arquivo de 2025 foi publicado vazio.
3. **156 sem número no endereço:** quando `numero_informado` é falso (cerca de 27%), o `id_local` representa a rua inteira. Tire esses registros antes de medir reincidência.
4. **Coordenadas do 156 faltam de forma não aleatória:** mais em iluminação e na RPA 1, e de 2024 em diante a cobertura cai para 23% a 50%. Por isso o recorte territorial principal é `bairro_oficial` e `rpa`.
5. **Códigos de serviço de 2012 a 2014** seguem outra tabela. Em 2012 existe o grupo guarda-chuva `CONSERVACAO`.
6. **Câmara:** `categoria` e `orgao` foram inferidos por palavra-chave (rótulo fraco). 33% das matérias não citam bairro (a N3 recuperou parte pela ementa: de 71,6% para 84,6% de cobertura nas indicações). Só as 54.813 indicações têm `camara_desfecho`.
7. **Ouvidoria:** não tem bairro. `ouv_resposta_antes_do_registro` marca um defeito da fonte, concentrado em 2024 e 2025. Os nomes de órgão mudam de formato em 2023 (a N3 harmonizou de 80 para 69).
8. **SEDEC:** a situação está congelada em 09/03/2024 (88,6% "em tramitação").
9. **Datas impossíveis** (1900, intervalos negativos) vieram das fontes. Filtre por `ano` e trate `dias_ate_movimento < 0` como defeito.
10. **Viés de notificação:** mais pedido não quer dizer mais problema. Use taxa por mil habitantes e filtre bairros com menos de 1.000 moradores (Recife e Santo Antônio distorcem).
11. **As três grafias:** o mesmo serviço aparece com grafias diferentes no 156. A N3 unificou as de terraplenagem (5.213 registros). Use o código do serviço, não o texto.

## Correções da N3 no pipeline

Elas nasceram no notebook da EDA (`Entregaveis/EntregaSemana12/N3_EDA_RecifeView_P5G8.ipynb`). A importação do backend já as aplica, como regras em `backend/app/domain/importacao/`, e conta cada uma no relatório da importação. Quando existir, o Processor deve reaproveitar essas regras em vez de reescrevê-las.

| Correção | Onde está |
|---|---|
| Bairro da Câmara recuperado pelo texto da ementa | Normalização |
| Nomes de órgão da Ouvidoria harmonizados | Normalização |
| Grafias de categoria do 156 unificadas | Normalização |
| 3.976 prazos negativos anulados, com a coluna `prazo_negativo` marcando a anulação | Normalização |
| Pedidos fechados no mesmo dia marcados | Normalização, com a alternância na tela de Prazos |
| Teto por local na reincidência | Alternância "endereços genéricos" na tela de Reincidência |
| Situação dos pedidos antigos do 156 como retrato da época | Regra dos arquivos recentes (ver as métricas abaixo) |
| 1.460 coordenadas fora do Recife anuladas | Não se aplica: a base analítica não guarda coordenadas |

Continua pendente harmonizar a situação entre as fontes. Hoje só as situações equivalentes do 156 são unificadas.

## Definições de métricas

Toda métrica exibida no painel precisa de uma definição única, registrada aqui antes de ir para a tela.

| Métrica | Definição | Situação |
|---|---|---|
| Reincidência | Hoje convivem três definições: 38,6% (156, 2026, logradouro + número + serviço, antes de deduplicar), 36,3% (156, 2026, depois de deduplicar, n = 54.755, usada no SR1) e 53,3% (156, 2015 a 2025, só com número no endereço, dataset único, H3 da N1/N3) | **Em aberto.** O grupo precisa escolher uma. O painel usa a terceira, chamada de "local repetido", e escreve a definição na tela |
| Duplicidade × reincidência | A N3 separa: repetição em até 7 dias é duplicidade; em 30 dias ou mais é reincidência | Proposta da N3 |
| Mesma ocorrência no pente fino | Mesmo bairro e categoria. Soma sozinho com endereço igual, número informado, mesmo serviço e até 7 dias. Vai para revisão com pontuação de 0,72 ou mais (local 60%, serviço 20%, tempo 15%, detalhe 5%). Com 30 dias ou mais, nunca é duplicidade | Proposta ([ADR 0009](adr/0009-formulario-publico-e-pente-fino.md)), pesos ainda sem calibração com dados rotulados |
| Prazo | Mediana e p90 de `dias_ate_movimento`, excluindo valores negativos. Pedido sem conclusão é tempo censurado, não zero nem descarte | Definido na N2 |
| Demanda per capita | Pedidos por mil habitantes por ano, só em bairros com 1.000 moradores ou mais | Definido na N2 |
| Resposta da Câmara | Percentual de indicações com `camara_desfecho = ENVIADO E COM RESPOSTA REGISTRADA` | Definido na N1 |
| Data de referência do estoque | A maior `data_do_retrato` entre as importações concluídas (`ouro.vw_referencia`). Antes era fixa em 07/10/2026 | Proposta ([ADR 0006](adr/0006-modelo-analitico-no-postgresql.md)) |
| Arquivos recentes | Os dois arquivos anuais mais novos de cada fonte. Reproduz 2025 e 2026 no 156 e 2024 e 2025 na Ouvidoria. Estoque aberto e fila só olham esses arquivos, porque a situação dos antigos é retrato da época | Proposta ([ADR 0006](adr/0006-modelo-analitico-no-postgresql.md)) |
| Identidade do registro | Sem protocolo, o registro se identifica pelo ano do arquivo, pelos campos da fonte e pela posição do conteúdo. Um arquivo só atualiza linhas do mesmo ano de arquivo; um pedido que aparece em dois arquivos anuais conta duas vezes, como no dataset | Proposta ([ADR 0006](adr/0006-modelo-analitico-no-postgresql.md)) |
| Sugestão de destino do encaminhamento | O órgão que o próprio registro aponta (quando está no catálogo de órgãos). Sem isso, o órgão mais citado nas indicações da Câmara do mesmo tema (`ouro.mv_camara_indicacoes`), se o tema tiver 30 indicações ou mais. O percentual mostrado é sobre todas as indicações do tema, inclusive as que não citam órgão | Proposta ([ADR 0011](adr/0011-encaminhamento-ao-orgao-e-retorno.md)). O órgão da Câmara é rótulo fraco |
| Prazo do encaminhamento | 30 dias corridos desde o envio para o órgão resolver ou devolver (Lei 13.460/2017, art. 16). Depois disso, o encaminhamento aberto conta como prazo vencido. "Dias até resolver" é a mediana entre o envio e o evento `resolvido` | Proposta ([ADR 0011](adr/0011-encaminhamento-ao-orgao-e-retorno.md)) |
| Índice de prioridade | AHP com quatro critérios por bairro. Os julgamentos entre os critérios são proposta do grupo, não validada pela Prefeitura, e podem ser mudados na tela | Proposta |

Ao mudar uma definição, atualize esta tabela, o serviço que a calcula e o texto da tela que a explica, no mesmo PR.
