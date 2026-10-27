# Design system

Como o RecifeView se parece e como ele fala. A identidade oficial vem do Drive (`AssetsVisuais/PaletaDeCores.txt` e o documento `IdentidadeVisual_RecifeView`). Todo o resto deste arquivo deriva dela e está marcado como **derivado**.

## Princípios

1. **O dado é o protagonista.** Branco predominante, texto preto, azul só onde se quer chamar a atenção. Se tudo é azul, nada se destaca.
2. **Um gráfico, uma pergunta.** Todo gráfico tem um título que é uma pergunta ou uma afirmação sobre o dado, não um rótulo genérico.
3. **Honestidade antes de impacto.** Mostrar percentil quando a média engana, avisar quando a cobertura é baixa, dizer que "sem resposta registrada" não é "não atendido".
4. **O gestor tem pouco tempo.** O mais importante fica no topo à esquerda; os detalhes ficam a um clique.
5. **Consistência entre telas.** A mesma fonte tem a mesma cor em todo lugar, o mesmo filtro fica no mesmo lugar e o mesmo número tem o mesmo formato.

## Cores

### Paleta oficial

| Token | Hex | Uso |
|---|---|---|
| `azul-principal` | `#0F62FE` | Títulos de destaque, botões, links, a série em foco num gráfico |
| `azul-claro` | `#EAF2FF` | Fundo de cartões de apoio, linha selecionada, faixa de filtros |
| `preto` | `#000000` | Texto principal |
| `branco` | `#FFFFFF` | Fundo da página, texto sobre azul |

### Derivadas da marca

| Token | Hex | Origem | Uso |
|---|---|---|---|
| `azul-marinho` | `#062A5F` | Palavra "Recife" do logo | Cabeçalho, extremo escuro da escala do mapa |
| `azul-escuro` | `#0043CE` | Tom mais escuro do azul principal | Hover e foco de botão, link visitado |

### Neutros (derivados)

| Token | Hex | Uso | Contraste sobre branco |
|---|---|---|---|
| `cinza-texto-secundario` | `#525252` | Subtítulos, descrições, texto sobre `azul-claro` | 7,8:1 |
| `cinza-texto-terciario` | `#6F6F6F` | Rótulos de eixo, notas de fonte | 5,0:1 |
| `cinza-contexto` | `#C6C6C6` | Séries de contexto (fora de foco), "sem dado" no mapa | 1,7:1, só para elementos gráficos |
| `cinza-borda` | `#E0E0E0` | Bordas de cartão, linhas de grade | 1,3:1, só decorativo |
| `cinza-fundo` | `#F4F4F4` | Fundo de tabela zebrada, área desabilitada | |

### Semânticas (derivadas)

Use só para estado, nunca como decoração.

| Token | Hex | Uso |
|---|---|---|
| `sucesso` | `#198038` | Confirmação de ação |
| `alerta-texto` | `#8E6A00` | Texto de aviso (dado parcial, cobertura baixa) |
| `alerta-fundo` | `#FCF4D6` | Fundo de faixa de aviso |
| `erro` | `#DA1E28` | Erro de carregamento, falha de login |

Uma variação percentual não é boa nem ruim por si só. Mais pedidos ao 156 pode ser mais problema ou mais confiança no canal. Não pinte variação de verde ou vermelho a menos que a direção desejada seja inequívoca, como "prazo p90 caiu".

### Cor fixa por fonte (derivada)

Quando várias fontes aparecem juntas, cada uma tem sempre a mesma cor, em todas as telas.

| Fonte | Hex |
|---|---|
| `156_EMLURB` | `#0F62FE` |
| `OUVIDORIA` | `#005D5D` |
| `CAMARA_REQUERIMENTOS` | `#B28600` |
| `DEFESA_CIVIL` | `#9F1853` |
| `SEDEC_CHAMADOS` | `#8A3800` |

O amarelo da Câmara (`#B28600`) tem contraste de 3,3:1: serve para barra e linha, mas não para texto pequeno. Num rótulo, use `preto` ao lado de uma marca de cor.

### Escala do mapa coroplético (derivada)

Escala sequencial de 5 classes, do claro ao escuro, toda dentro da família de azuis da marca:

| Classe | Hex |
|---|---|
| 1 (menor) | `#EAF2FF` |
| 2 | `#A6C8FF` |
| 3 | `#4589FF` |
| 4 | `#0F62FE` |
| 5 (maior) | `#062A5F` |

- Bairro sem dado: `cinza-contexto` (`#C6C6C6`) com hachura diagonal, e o item "sem dado" na legenda. Nunca use a classe mais clara para "sem dado".
- Se precisar de 7 classes, intercale `#78A9FF` (entre 2 e 3) e `#0043CE` (entre 4 e 5).
- Escala divergente (acima ou abaixo do esperado, por exemplo um resíduo): azul de um lado, `#8A3800` do outro, branco no centro. Combine com o grupo antes de usar.

### Contraste: cuidados que já foram medidos

- `azul-principal` sobre `branco`: 5,0:1. Pode ser usado em texto de qualquer tamanho.
- `azul-principal` sobre `azul-claro`: 4,4:1. **Não passa** para texto pequeno; só para texto de 19px ou mais em negrito.
- `cinza-texto-terciario` sobre `azul-claro`: 4,5:1, no limite. Sobre `azul-claro`, use `cinza-texto-secundario`.

## Tipografia

Montserrat, carregada do Google Fonts com os pesos 400, 500, 600 e 700.

| Papel | Tamanho | Peso | Uso |
|---|---|---|---|
| Título da página | 28px | 700 | Um por tela |
| Título de seção | 20px | 700 | Grupo de gráficos |
| Título de gráfico | 16px | 600 | Pergunta ou afirmação do gráfico |
| Corpo | 14px | 400 | Texto geral do painel |
| Secundário | 13px | 400 | Subtítulo de gráfico, descrição |
| Legenda e eixo | 12px | 500 | Rótulos de eixo, legenda, nota de fonte |
| Número de KPI | 32px | 700 | Valor principal do cartão |

- Números em tabela, KPI e eixo usam algarismos tabulares (`font-variant-numeric: tabular-nums`), para alinharem em coluna.
- Altura de linha: 1,5 no corpo e 1,2 nos títulos.
- Nada em caixa alta corrida, exceto siglas.

## Espaço, forma e profundidade

- Espaçamento em múltiplos de 4px: 4, 8, 12, 16, 24, 32, 48, 64.
- Raio: 4px em campos e botões, 8px em cartões. Nada de cantos muito arredondados.
- Profundidade com borda `cinza-borda` de 1px, não com sombra. Sombra só em elemento flutuante (tooltip, menu aberto), e discreta.
- Grade de 12 colunas, com 24px entre colunas. Largura máxima do conteúdo: 1440px.

## Layout do painel

O mockup 04 da pasta `MockupsDashboard` serve de referência de estrutura. Os números dele são fictícios.

```
┌──────────────────────────────────────────────────────────────┐
│ logo · navegação entre telas                       usuário   │  cabeçalho
├──────────────────────────────────────────────────────────────┤
│ Período · RPA · Bairro · Serviço · Situação · Fonte          │  filtros globais (fixos)
├──────────────────────────────────────────────────────────────┤
│ Título da tela                                               │
│ A pergunta que a tela responde, em uma linha                 │
│                                                              │
│ [KPI] [KPI] [KPI] [KPI]                                      │  no máximo 4
│                                                              │
│ ┌──────────────────────────┐ ┌─────────────────────────────┐ │
│ │ gráfico principal        │ │ gráfico de apoio            │ │
│ └──────────────────────────┘ └─────────────────────────────┘ │
│ Fonte: ... · Período: ... · n = ...                          │
└──────────────────────────────────────────────────────────────┘
```

- A barra de filtros fica fixa no topo e vale para todas as telas. Filtro aplicado mostra um resumo legível ("RPA 3 · 2021 a 2025") e um jeito de limpar.
- O público é um gestor no computador. Desenhe primeiro para 1280px ou mais e garanta leitura em tablet. No celular, basta que os KPIs e as tabelas sejam legíveis.

## Componentes

- **Cartão de KPI:** rótulo, valor, contexto (período e comparação) e fonte em uma linha. Sem ícone decorativo.
- **Botão primário:** fundo `azul-principal` e texto `branco`. Só um botão primário por área.
- **Botão secundário:** borda `azul-principal`, texto `azul-principal` e fundo `branco`.
- **Tabela:** cabeçalho em 12px/600, números alinhados à direita, linhas de 40px, zebra opcional com `cinza-fundo`.
- **Estados:** toda área de dado tem os estados carregando (esqueleto com a forma do gráfico), vazio ("Nenhuma demanda para estes filtros") e erro (o que aconteceu e como tentar de novo).
- **Aviso de dado parcial:** faixa com `alerta-fundo` e `alerta-texto`, curta e específica: "Coordenadas disponíveis para 26% dos pedidos de 2024. O mapa usa bairro."

## Gráficos (Recharts)

Regras gerais:

- O título diz o que olhar: "Prazo p90 do 156 quase dobrou depois de 2020", não "Prazos por ano".
- Abaixo de todo gráfico vai a nota com fonte, período, filtros e n, em 12px e `cinza-texto-terciario`.
- Destaque por contraste: a série em foco em `azul-principal` e as demais em `cinza-contexto`. É o uso de atributos pré-atentivos que a N8 pede.
- Rótulo direto na linha ou na barra sempre que couber; a legenda separada é o último recurso.
- Grade só horizontal, em `cinza-borda`. Sem borda na área do gráfico.
- Eixo Y de barras começa em zero. Escala logarítmica só quando os dados pedirem (prazos, per capita da Defesa Civil), e com "escala log" escrito no eixo.
- Animação curta (até 300ms) ou nenhuma.
- Tooltip com fundo `branco`, borda `cinza-borda`, valores formatados em pt-BR e a unidade escrita.

Qual gráfico para qual pergunta:

| Pergunta | Gráfico |
|---|---|
| Como a demanda evolui no tempo | Linha (mês ou ano) |
| Quais serviços ou bairros lideram | Barra horizontal ordenada |
| Quanto tempo leva | Mediana e p90 em barras ou pontos; boxplot quando houver espaço. Nunca só a média |
| Para onde as demandas vão | Sankey (categoria → órgão) |
| Onde a resposta se perde | Funil (apresentada → enviada → com resposta) |
| Relação entre dois indicadores por bairro | Dispersão com linha de tendência e outliers nomeados |
| Padrão por mês e categoria | Heatmap |
| Onde, no território | Mapa coroplético (abaixo) |

Não use: pizza com mais de 3 fatias, rosca, gráfico 3D, gauge, eixo duplo e gradiente dentro de barra.

## Mapas (Leaflet)

- A unidade principal é o bairro oficial (94 bairros), com agrupamento opcional por RPA. As coordenadas do 156 faltam de forma não aleatória, então o mapa de pontos só pode entrar como camada secundária, com o aviso de cobertura.
- Mapear taxa, não contagem: pedidos por mil habitantes, filtrando bairros com menos de 1.000 moradores (ver [dados.md](dados.md#cuidados-antes-de-usar)).
- 5 classes por quantis, com os limites escritos na legenda ("12 a 30 por mil hab.").
- Mapa de fundo claro e discreto (estilo Positron), ou nenhum. Mantenha a atribuição (OpenStreetMap e o provedor do mapa base).
- Contorno dos bairros em `branco` com 1px; bairro em foco com contorno `preto` de 2px.
- Hover mostra o nome do bairro, o valor e a RPA. O clique seleciona o bairro no filtro global.
- Ao lado do mapa vai sempre uma tabela ordenada com os mesmos valores. Ela é a alternativa acessível e o jeito mais rápido de ler os extremos.
- Os dois mapas de prioridade (serviço urbano e emergência) ficam lado a lado, com a mesma escala de cores e legendas independentes.

## Texto e voz

- Direto, em português claro, sem jargão de TI para o gestor. "Pedidos" e "demandas", não "registros" nem "tickets".
- Números no padrão pt-BR: `1.377.158`, `36,3%`, `6,8 dias`. Valores grandes em KPI podem abreviar ("1,4 mi") com o número completo no tooltip.
- Datas `dd/mm/aaaa`; meses `out/2026`; períodos `2021 a 2025`.
- Nenhum travessão (—) nem meia-risca (–) em texto de interface. Use vírgula, dois-pontos, parênteses ou ponto: "RPA 3 (Norte)", "Prazos por serviço", "Carregando...". A regra completa está em [padroes-de-codigo.md](padroes-de-codigo.md#travessão).
- Diga o que o número é e o que ele não é. "Sem resposta registrada" não quer dizer "não atendido". Ao citar a reincidência, diga a definição.
- Termos de domínio sempre iguais: RPA, bairro, serviço, órgão, Central 156, Ouvidoria, Defesa Civil, SEDEC, Câmara Municipal.

## Acessibilidade

- Meta: WCAG 2.2 nível AA.
- Texto com contraste de pelo menos 4,5:1; elementos gráficos com pelo menos 3:1.
- A informação nunca depende só da cor: use rótulo, padrão ou posição.
- Tudo funciona pelo teclado, com foco visível (contorno de 2px em `azul-escuro`).
- Todo gráfico tem uma alternativa em texto ou tabela.

## O que evitar

A interface e os documentos não podem ter cara de template genérico nem de texto gerado automaticamente. Evite:

- Emoji em interface, documentação ou commit.
- Travessão e meia-risca, em qualquer texto.
- Gradientes (sobretudo roxo e azul), glassmorphism, neon, fundo escuro "tech" e brilhos.
- Ícone decorativo em todo título ou cartão. Ícone só quando ajuda a reconhecer uma ação (filtro, download, fechar).
- Frases de efeito e enchimento: "Insights poderosos", "Transformando dados em decisões", "Bem-vindo(a)!", "Explore o poder de...".
- Cantos muito arredondados, sombras grandes e cartões flutuando.
- Ilustração genérica de pessoas, cidade ou robôs. A identidade já tem logo e skyline próprios.
- Dado de exemplo ou mockup apresentado como real. Número fictício só em protótipo, com a marcação "dado fictício".
- Texto genérico que serviria a qualquer cidade. Cite bairros, RPAs, órgãos e serviços reais do Recife.
- Excesso de negrito e de listas com marcador em texto corrido. Prefira frases.

## Assets

- O logo para o README está em [assets/logo-recifeview.png](assets/logo-recifeview.png).
- As versões branca, ícone e wordmark ficam em Drive › `AssetsVisuais/Marca`. São PNGs renderizados, não vetores: ao trazer um para o frontend, use a maior resolução disponível e nunca o redesenhe.
- O favicon sai do ícone do mapa em rede (`Marca/01` a `03`). Escolha um com o grupo.
