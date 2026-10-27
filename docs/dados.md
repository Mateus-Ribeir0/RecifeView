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

Dados de apoio: IBGE Censo 2022 por bairro (94 bairros, 1.488.920 habitantes), malha de bairros e RPAs em GeoJSON e o catálogo de serviços do Conecta Recife (840 serviços).

Papel de cada fonte (N2): o **núcleo** é formado por 156/Emlurb, Ouvidoria e Câmara; o **complemento**, por SEDEC e Defesa Civil; o **apoio**, por IBGE, malha e catálogo.

## Fontes

| Fonte | Origem | Licença ou natureza |
|---|---|---|
| 156/Emlurb, Defesa Civil, Ouvidoria, malha de bairros | Portal de Dados Abertos do Recife (dados.recife.pe.gov.br), baixados em 07/10/2026 | ODbL |
| SEDEC Chamados | Cópia de 09/03/2024 no Internet Archive (o dataset foi retirado do portal) | Dado público arquivado |
| Câmara Municipal | Sistema público SAGL (publico.recife.pe.leg.br), coletado em 07 e 08/10/2026 | Dado público |
| IBGE | Censo 2022, tabelas 9922, 9923 e 10206 | Dado público |

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

## Correções da N3 que ainda precisam ir para o pipeline

Hoje elas existem só no notebook da EDA (`Entregaveis/EntregaSemana12/N3_EDA_RecifeView_P5G8.ipynb`). O Processor deve reproduzi-las:

- Bairro da Câmara recuperado pelo texto da ementa.
- Nomes de órgão da Ouvidoria harmonizados.
- Grafias de categoria do 156 unificadas.
- 1.460 coordenadas fora do Recife e 3.976 prazos negativos anulados, com uma coluna marcando a anulação.
- Marcar os pedidos fechados no mesmo dia, pôr um teto por local na reincidência e tratar a situação dos pedidos antigos do 156 como retrato da época.
- Harmonizar a situação entre as fontes.

## Definições de métricas

Toda métrica exibida no painel precisa de uma definição única, registrada aqui antes de ir para a tela.

| Métrica | Definição | Situação |
|---|---|---|
| Reincidência | Hoje convivem três definições: 38,6% (156, 2026, logradouro + número + serviço, antes de deduplicar), 36,3% (156, 2026, depois de deduplicar, n = 54.755, usada no SR1) e 53,3% (156, 2015 a 2025, só com número no endereço, dataset único, H3 da N1/N3) | **Em aberto.** O grupo precisa escolher uma |
| Duplicidade × reincidência | A N3 separa: repetição em até 7 dias é duplicidade; em 30 dias ou mais é reincidência | Proposta da N3 |
| Prazo | Mediana e p90 de `dias_ate_movimento`, excluindo valores negativos. Pedido sem conclusão é tempo censurado, não zero nem descarte | Definido na N2 |
| Demanda per capita | Pedidos por mil habitantes por ano, só em bairros com 1.000 moradores ou mais | Definido na N2 |
| Resposta da Câmara | Percentual de indicações com `camara_desfecho = ENVIADO E COM RESPOSTA REGISTRADA` | Definido na N1 |

Ao mudar uma definição, atualize esta tabela, o serviço que a calcula e o texto da tela que a explica, no mesmo PR.
