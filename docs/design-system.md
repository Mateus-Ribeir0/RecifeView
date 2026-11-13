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
| `azul-marinho` | `#062A5F` | Palavra "Recife" do logo | Cabeçalho da gestão, extremo escuro da escala do mapa |
| `azul-escuro` | `#0043CE` | Tom mais escuro do azul principal | Hover e foco de botão, link visitado |

### Neutros (derivados)

| Token | Hex | Uso | Contraste sobre branco |
|---|---|---|---|
| `cinza-texto-secundario` | `#525252` | Subtítulos, descrições, texto sobre `azul-claro` | 7,8:1 |
| `cinza-texto-terciario` | `#6F6F6F` | Rótulos de eixo, notas de fonte | 5,0:1 |
| `cinza-borda-de-campo` | `#8D8D8D` | Borda de campo de formulário e de botão de filtro | 3,3:1, passa o mínimo de 3:1 para componentes |
| `cinza-contexto` | `#C6C6C6` | Séries de contexto (fora de foco), "sem dado" no mapa | 1,7:1, só para elementos gráficos |
| `cinza-borda` | `#E0E0E0` | Bordas de cartão, linhas de grade | 1,3:1, só decorativo |
| `cinza-fundo` | `#F4F4F4` | Fundo de tabela zebrada, área desabilitada | |

### Semânticas (derivadas)

Use só para estado, nunca como decoração.

| Token | Hex | Uso |
|---|---|---|
| `sucesso` | `#198038` | Confirmação de ação, requisito atendido |
| `sucesso-fundo` | `#DEFBE6` | Fundo de aviso de sucesso |
| `alerta-texto` | `#8E6A00` | Texto de aviso (dado parcial, cobertura baixa) |
| `alerta-fundo` | `#FCF4D6` | Fundo de faixa de aviso |
| `erro` | `#DA1E28` | Erro de carregamento, falha de login, mensagem de campo |
| `erro-fundo` | `#FFF1F1` | Fundo de aviso de erro (o texto continua `preto`) |

Os tokens estão implementados em `frontend/src/ui/theme/tokens.css`, com o prefixo `--cor-`.

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
| `FORMULARIO_PUBLICO` | `#393939` |

O amarelo da Câmara (`#B28600`) tem contraste de 3,3:1: serve para barra e linha, mas não para texto pequeno. Num rótulo, use `preto` ao lado de uma marca de cor.

Essas cores são os tokens `--cor-fonte-*` de `tokens.css`. Medidas com o validador de paleta, elas não passam em tudo: Defesa Civil e SEDEC ficam a Delta E 12,3 (o mínimo é 15) e a Ouvidoria tem pouco croma. Enquanto o grupo não trocar a paleta, identidade por fonte nunca fica só na cor: as séries usam marcadores de formas diferentes e sempre têm legenda.

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

### Cabeçalho por área de acesso

O cabeçalho diz em que área a pessoa está, antes de qualquer texto. Os dois tokens ficam em `tokens.css` e apontam para cores que já existem:

| Token | Aponta para | Onde |
|---|---|---|
| `cabecalho-da-cidade` | `azul-principal` (`#0F62FE`) | Entrada do cidadão (`/entrar`, `/cadastrar`, `/recuperar-senha`) e área do cidadão (`/cidade`) |
| `cabecalho-da-gestao` | `azul-marinho` (`#062A5F`) | Entrada da gestão (`/entrar/gestao`, `/entrar/ajuda`), painel e a faixa "Trabalha na gestão pública?" no fim da página inicial |

Cor nunca é o único sinal: as duas áreas mostram um selo com borda branca ao lado do logo ("Área do cidadão" ou "Área da gestão"), e a entrada da gestão tem título e texto próprios. Em tela estreita (abaixo de 720px no painel e de 900px na área do cidadão) o selo sai, e o tom do cabeçalho segue marcando a área. As telas de entrada também mudam o fundo do painel lateral: foto do Recife na do cidadão e malha dos bairros sobre azul-marinho na da gestão.

### Seleção (derivada)

| Token | Hex | Uso |
|---|---|---|
| `selecao` | `#FF832B` | Só o elemento que a pessoa clicou (bairro no mapa, ponto da dispersão). Contrasta com a escala azul, e por isso não serve para mais nada |

### Contraste: cuidados que já foram medidos

- `azul-principal` sobre `branco`: 5,0:1. Pode ser usado em texto de qualquer tamanho.
- `azul-principal` sobre `azul-claro`: 4,4:1. **Não passa** para texto pequeno; só para texto de 19px ou mais em negrito.
- `cinza-texto-terciario` sobre `azul-claro`: 4,5:1, no limite. Sobre `azul-claro`, use `cinza-texto-secundario`.
- Rótulo de seção sobre `azul-claro`: use `azul-escuro` (6,9:1), não `azul-principal`.
- `sucesso` e `erro` sobre `cinza-fundo`: 4,6:1 e 4,5:1. Passam, mas no limite: não clareie esses fundos.
- `alerta-texto` sobre `alerta-fundo`: 4,5:1.
- `branco` sobre `azul-principal`: 5,0:1. Texto em faixa azul sempre em branco puro, sem transparência.
- `branco` a 85% sobre `azul-marinho`: 10,4:1. Pode ser usado para texto secundário no cabeçalho e no rodapé.

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

Na página inicial pública, que é lida e não operada, a escala cresce:

| Papel | Tamanho | Peso | Token |
|---|---|---|---|
| Título de abertura | 52px (34px no celular) | 700 | `--texto-destaque` |
| Título de seção | 36px (28px no celular) | 700 | `--texto-secao` |
| Texto de abertura | 18px | 400 | `--texto-abertura` |
| Corpo | 16px | 400 | `--texto-corpo` |

A página pública tem cinco abas, com endereço próprio: Início, Como funciona, A cidade em números, Acompanhar um pedido e Relatar um problema. Ela é a vitrine do produto, então pode usar o que o painel não usa:

- **Foto:** a do banner `AssetsVisuais/BannersHome/07`, já no azul da marca, em `ui/assets/imagens/`. Texto sobre ela sempre em branco puro.
- **Capturas:** telas reais do painel em `ui/assets/capturas/`, geradas sem dado fictício. Se a tela usar dado de demonstração, a nota diz "dado fictício".
- **Ícones de apoio:** em etapas, temas e cartões, quando ajudam a reconhecer o assunto. No painel, continua valendo a regra de ícone só para ação e navegação.
- **Movimento:** entrada ao rolar (`Aparecer`), contagem de números (`ContadorAnimado`) e barras que crescem quando aparecem, com `--duracao-de-entrada` e `--curva-de-entrada`. Quem pede menos movimento no sistema (`prefers-reduced-motion`) vê tudo pronto, sem animação.

- Números em tabela, KPI e eixo usam algarismos tabulares (`font-variant-numeric: tabular-nums`), para alinharem em coluna.
- Altura de linha: 1,5 no corpo e 1,2 nos títulos.
- Nada em caixa alta corrida, exceto siglas.

## Espaço, forma e profundidade

- Espaçamento em múltiplos de 4px: 4, 8, 12, 16, 24, 32, 48, 64, e 96 só entre seções da página inicial.
- Raio: 4px em campos e botões, 8px em cartões. Nada de cantos muito arredondados.
- Profundidade com borda `cinza-borda` de 1px, não com sombra. Sombra só em elemento flutuante (tooltip, menu aberto), e discreta.
- Grade de 12 colunas, com 24px entre colunas. Largura máxima do conteúdo: 1440px no painel e 1200px na página inicial, para as linhas de texto não ficarem longas demais.
- Margem lateral de 16px no celular e 32px a partir de 720px.

## Layout do painel

O mockup 04 da pasta `MockupsDashboard` serve de referência de estrutura. Os números dele são fictícios.

```
┌──────────────────────────────────────────────────────────────┐
│ menu · logo                                        usuário   │  cabeçalho
├──────┬───────────────────────────────────────────────────────┤
│ ícone│ Período · RPA · Bairro · Categoria · Limpar           │  filtros (fixos)
│ ícone├───────────────────────────────────────────────────────┤
│ ícone│ Título da tela                          ações da tela │
│ ─────│ Uma frase com a pergunta da tela                      │
│ ícone│ Selos das fontes · Sobre esta tela                    │
│ ícone│                                                       │
│ ─────│ [KPI] [KPI] [KPI] [KPI]                  no máximo 4  │
│ ícone│                                                       │
│ ícone│ ┌───────────────────────┐ ┌─────────────────────────┐ │
│      │ │ gráfico principal     │ │ gráfico de apoio        │ │
│      │ │ Como ler · Fonte · n  │ │ Como ler · Fonte · n    │ │
│      │ └───────────────────────┘ └─────────────────────────┘ │
└──────┴───────────────────────────────────────────────────────┘
```

- A barra lateral (fundo `azul-claro`) tem ícone e rótulo. Telas com pendência mostram um contador à direita do rótulo, em `alerta-fundo` com `alerta-texto` (Encaminhamentos: o que pede ação; Contribuições: duplas do pente fino). O contador some quando é zero e tem texto para leitor de tela ("3 encaminhamentos pedem ação"). O botão de menu do cabeçalho alterna entre aberta (`--largura-da-lateral`) e recolhida só com ícones (`--largura-da-lateral-recolhida`), e a escolha fica salva. Abaixo de 1040px, ela vira gaveta, com o fundo escurecido e um X para fechar. A decisão está na [ADR 0008](adr/0008-navegacao-lateral-com-filtros.md) (proposta).
- A linha de filtros fica fixa acima do conteúdo e mostra só os filtros que a tela aplica. Filtro em uso fica em `azul-claro`, com o valor escrito, e aparece "Limpar". Telas sem filtros não têm a linha.
- Texto corrido não fica na tela: o cabeçalho tem uma frase, o detalhe vai em "Sobre esta tela" e a explicação de cada gráfico vai em "Como ler", que abre sob demanda. A nota de fonte, período e n continua sempre visível.
- Telas com assuntos diferentes se dividem em abas, em vez de crescer para baixo.
- A War Room tem cinco KPIs, um a mais que o limite, porque o quadro inteiro é a leitura do dia.
- O público é um gestor no computador. Desenhe primeiro para 1280px ou mais e garanta leitura em tablet. No celular, basta que os KPIs e as tabelas sejam legíveis.

## Componentes

- **Cartão de KPI:** rótulo, valor, contexto e, quando houver, um visual (`Medidor` para proporção, `Sparkline` para tendência). Rótulo, valor, contexto e visual se alinham entre os cartões da mesma linha. Sem ícone decorativo.
- **Cartões lado a lado:** têm sempre a mesma altura, com o rodapé (Como ler e nota) preso embaixo.
- **Ícone:** só em `ui/components/Icone.tsx`, em traço de 1,75px. Serve para reconhecer um destino da navegação ou uma ação, nunca para enfeitar título.
- **Botão primário:** fundo `azul-principal` e texto `branco`. Só um botão primário por área.
- **Botão secundário:** borda `azul-principal`, texto `azul-principal` e fundo `branco`.
- **Tabela:** cabeçalho em 12px/600, números alinhados à direita, linhas de 40px, zebra opcional com `cinza-fundo`.
- **Estados:** toda área de dado tem os estados carregando (esqueleto com a forma do gráfico), vazio ("Nenhuma demanda para estes filtros") e erro (o que aconteceu e como tentar de novo).
- **Aviso de dado parcial:** faixa com `alerta-fundo` e `alerta-texto`, curta e específica: "Coordenadas disponíveis para 26% dos pedidos de 2024. O mapa usa bairro."

## Área do cidadão

Quem tem conta de cidadão vê os relatos da cidade e os números do próprio bairro, sem nada que identifique quem relatou (o que cada nível vê está na [ADR 0010](adr/0010-contas-de-cidadao-e-niveis-de-acesso.md)).

- **Navegação:** abas no cabeçalho azul (Relatos da cidade, Meus relatos, Meus pedidos, Meu bairro, Relatar um problema), sem barra lateral e sem linha de filtros. A escolha do bairro e do tema fica no topo da lista.
- **Cartão de ocorrência:** categoria, rua (só quando é uma via reconhecida da base oficial), faixa de numeração ("entre 100 e 199"), bairro, há quanto tempo, quantas pessoas relataram e o selo de situação. O texto que a pessoa escreveu nunca aparece.
- **Selo de situação:** texto sempre escrito, com a cor como reforço. Recebido em `cinza-fundo`; Em análise em `alerta-fundo` com `alerta-texto`; No painel da gestão em `azul-claro` com `azul-escuro`; Coberto por pedido oficial em `sucesso-fundo` com `sucesso`. A explicação de cada situação fica na própria tela.
- **Andamento em Meus relatos:** três etapas lado a lado (Recebido, Em análise pela gestão e No painel da gestão, ou Já tem pedido oficial no lugar da última), cada uma com borda superior de 3px e um círculo: etapa feita em `azul-principal` com marca de confirmado, etapa atual em `azul-principal` com o miolo branco e etapa que falta em `cinza` (`borda-de-campo`). O nome da etapa vem sempre escrito, e abaixo vai a explicação da situação atual. No desktop, uma coluna em `azul-claro` explica as quatro situações.
- **Escolha do bairro no mapa:** o mapa marca só se o bairro tem relato ou não (sem escala graduada) e o bairro escolhido fica em `selecao`.
- **Andamento de um pedido** (`/acompanhar` e Meus pedidos): cartão com a fonte, o protocolo, o assunto e a situação na fonte. Se a gestão encaminhou, uma faixa em `azul-claro` diz para qual órgão, com o selo da etapa e as etapas lado a lado (borda superior de 3px em `azul-principal`). A justificativa da gestão e a observação do órgão nunca aparecem para o cidadão.
- **Selo do encaminhamento:** Enviado, sem resposta em `alerta-fundo` com `alerta-texto`; Recebido pelo órgão em `azul-claro` com `azul-escuro`; Resolvido em `sucesso-fundo` com `sucesso`; Falha no envio em `erro-fundo`; Devolvido em `cinza-fundo`. "Prazo vencido" vem escrito no selo, nunca só pela cor.
- **Celular primeiro:** ao contrário do painel, esta área é desenhada para 390px e alargada até 1280px.

## Gráficos (Recharts)

Regras gerais:

- O título diz o que olhar: "Prazo p90 do 156 quase dobrou depois de 2020", não "Prazos por ano".
- Abaixo de todo gráfico vai a nota com fonte, período, filtros e n, em 12px e `cinza-texto-terciario`.
- Destaque por contraste: a série em foco em `azul-principal` e as demais em `cinza-contexto`. É o uso de atributos pré-atentivos que a N8 pede.
- Rótulo direto na linha ou na barra sempre que couber; a legenda separada é o último recurso.
- Grade só horizontal, em `cinza-borda`. Sem borda na área do gráfico.
- Eixo Y de barras começa em zero. Escala logarítmica só quando os dados pedirem (prazos, per capita da Defesa Civil), e com "escala log" escrito no eixo.
- Animação curta (até 300ms) ou nenhuma. Na página pública, a barra pode crescer em até 1s quando entra na tela, porque ali o gráfico é lido uma vez, não operado.
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
- Contorno dos bairros em `branco` com 1px. O contorno de foco do navegador é desligado nos polígonos, porque ele desenha um retângulo em volta do bairro.
- Hover reforça o contorno e mostra o nome do bairro, o valor e a RPA. O clique seleciona: o bairro fica em `cor-selecao`, com contorno `preto` e o nome fixo, e os demais ficam atenuados. Clicar de novo tira a seleção. O detalhe abre junto do mapa, sem mudar o filtro global, e o mesmo bairro aparece em `cor-selecao` nos outros gráficos da tela.
- Ao lado do mapa vai sempre uma tabela ordenada com os mesmos valores. Ela é a alternativa acessível e o jeito mais rápido de ler os extremos.
- Os dois mapas de prioridade (serviço urbano e emergência) ficam lado a lado, com a mesma escala de cores e legendas independentes.

### Mapa sem dado (página inicial, telas de acesso e área do cidadão)

Fora das telas de dados, o mapa dos bairros é só referência geográfica, desenhado em SVG (`ui/map/MapaDosBairros.tsx`), sem Leaflet e sem mapa de fundo:

- **Sobre branco:** preenchimento `azul-claro` com traço `#4589FF` de 0,75px, como um desenho de linhas. RPA escolhida em `#A6C8FF` e bairro sob o mouse em `azul-principal`, os dois com traço branco.
- **Sobre `azul-principal`:** preenchimento branco a 6% e traço branco a 40%, puramente decorativo (`aria-hidden`).
- Nunca pinte esse mapa com a escala sequencial por RPA ou por qualquer categoria: quem vê cor graduada lê quantidade.
- A legenda diz que a malha é da Prefeitura do Recife, Portal de Dados Abertos, licença ODbL.

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
- Ícone decorativo em todo título ou cartão. No painel, ícone só quando ajuda a reconhecer uma ação ou um destino da navegação (filtro, download, fechar, itens do menu). A exceção da página pública está em [Tipografia](#tipografia).
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
