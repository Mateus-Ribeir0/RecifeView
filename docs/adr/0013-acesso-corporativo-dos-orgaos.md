# 0013. Dar acesso próprio aos órgãos, mostrar o mesmo problema em toda a plataforma e avisar dentro dela

- **Status:** proposta
- **Data:** 19/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi pedida em 19/11/2026

## Contexto

A [ADR 0011](0011-encaminhamento-ao-orgao-e-retorno.md) fechou o ciclo com um link por encaminhamento: o órgão abre `/retorno/<token>`, marca a etapa e pronto. O link resolve um caso de cada vez, mas deixa três lacunas:

1. **O órgão não tem visão do conjunto.** Quem trabalha na Emlurb ou na Compesa não vê o que já recebeu, o que está vencendo, o que resolveu nem onde se concentram os pedidos. Cada link é uma janela isolada, que vence em 60 dias.
2. **O mesmo problema chega várias vezes.** O 156 registra o mesmo buraco ou o mesmo vazamento em dias seguidos: na base, 53,3% dos pedidos do 156 de 2015 a 2025 com número no endereço repetem um local já pedido (a definição "local repetido" de [dados.md](../dados.md#definições-de-métricas)). Se a gestão encaminha dois desses registros, o órgão trata duas vezes e o cidadão de um deles não fica sabendo da solução do outro.
3. **O cidadão recebe a etapa, mas não a resposta.** A ADR 0011 manda ao cidadão só o nome da etapa, porque a observação do órgão é texto interno. Quem relatou fica sabendo que "foi resolvido", sem saber o que foi feito, e o aviso só existe por e-mail.

O grupo também pediu que a administração da Prefeitura consiga comparar os órgãos entre si e contrastar o que cada um informa com o que os dados mostram depois.

## Opções consideradas

**Como o órgão entra**

| Opção | A favor | Contra |
|---|---|---|
| Só o link por encaminhamento (como na ADR 0011) | Nada a manter | Sem visão do conjunto, sem histórico, sem resposta em grupo |
| Conta da gestão para cada órgão | Reaproveita o painel | O órgão veria todos os órgãos e a base inteira, inclusive a fila de prioridade da Prefeitura |
| Perfil próprio (`CORPORATIVO`), preso a um órgão, criado pela administração | Cada órgão vê só o que é dele; a Prefeitura controla quem entra | Uma área nova para manter |

**Como a conta chega ao responsável**

| Opção | A favor | Contra |
|---|---|---|
| Senha temporária por e-mail | Igual à linha de comando de hoje | A senha fica no e-mail; quem cria a conta poderia vê-la |
| Link de convite com validade, em que a pessoa define a senha | Nenhuma senha trafega; quem cria a conta nunca a conhece | Mais uma tabela (convites) |

**Quanto do local o órgão vê**

| Opção | A favor | Contra |
|---|---|---|
| Endereço exato do relato | Facilita achar o ponto | O endereço pode ser o de quem relatou; contraria a [ADR 0010](0010-contas-de-cidadao-e-niveis-de-acesso.md) e a ADR 0011 |
| Bairro, rua da lista oficial e faixa de numeração de 100 em 100 | O mesmo que a mensagem da ADR 0011 já manda; basta para localizar um trecho | Pode exigir uma visita para achar o ponto exato |

**Como reconhecer o mesmo problema**

| Opção | A favor | Contra |
|---|---|---|
| Agrupar à mão, pela gestão | Sem erro de regra | Retrabalho, que é justamente o que se quer evitar |
| Regra nova só para encaminhamentos | Livre para calibrar | Duas regras diferentes para a mesma pergunta |
| A regra do pente fino ([ADR 0009](0009-formulario-publico-e-pente-fino.md)), aplicada aos encaminhamentos | Uma definição só, já documentada e testada | Os pesos ainda não foram calibrados com dados rotulados |

## Decisão

**1. Perfil corporativo.** Nasce o perfil `CORPORATIVO`, com o órgão gravado na conta (`app.usuario.orgao`, um dos órgãos do catálogo da ADR 0011). A área fica em `/corporativo` e a entrada em `/entrar/corporativo`. Cada perfil continua vendo só a sua área: as rotas da gestão recusam o corporativo, as de `/corporativo` recusam os outros perfis e as da cidade passam a exigir o perfil de cidadão (antes bastava não ser da gestão).

**2. Quem cria.** Só o perfil Administração (`ADMINISTRADOR`) cria, edita, reenvia convite, desativa, reativa e exclui acessos corporativos, na tela "Acessos corporativos" do painel. A Gestão pública (`GESTOR`) vê a lista. Criar a conta manda ao responsável um convite com o link `/convite/<token>` (32 bytes aleatórios, guardados como hash SHA-256, válidos por 7 dias e de uso único). Pelo link, a pessoa define a senha e já entra. Reenviar invalida o convite anterior. Excluir apaga nome e e-mail e mantém a linha para a auditoria, como na exclusão da conta de cidadão. A linha de comando também cria a conta corporativa, com senha temporária, para o ambiente local.

**3. O que o órgão vê.** Só os encaminhamentos feitos ao próprio órgão, menos os que falharam no envio (esses voltam para a gestão reenviar). O local é o da ADR 0011: bairro, RPA e, nos relatos do formulário, a rua da lista oficial com a faixa de numeração. De quem acompanha o pedido, só a contagem. O órgão também vê a parte da base aberta que cita o seu nome (volume por ano e fonte, bairros, temas e situação na fonte), sem as ações proativas da Defesa Civil, a partir da view `ouro.mv_demanda_por_orgao`.

**4. Como o órgão responde.** As etapas são as da ADR 0011, com dois acréscimos:

- **Em atendimento** (`recebido`) aceita uma previsão de conclusão e pode ser repetido para atualizar o andamento.
- Toda resposta pode levar uma **resposta ao cidadão** (até 500 caracteres, sem CPF, telefone ou e-mail), separada da nota interna. Na área corporativa, ela é obrigatória para resolver e para devolver. É o único texto do órgão que chega a quem pediu. A nota interna continua só com a gestão e o órgão.

O link da ADR 0011 continua valendo para órgão sem conta. Órgão com acesso ativo e sem canal configurado recebe pela própria plataforma (canal `plataforma`), sem arquivo na caixa de saída local. Órgão com canal configurado (e-mail ou webhook) continua recebendo por ele e também vê tudo na área corporativa.

**5. Mesmo problema.** Dois encaminhamentos tratam do mesmo problema quando a regra do pente fino os classifica como "mesma ocorrência" ou "provável": mesma fonte (o `id_local` só vale dentro da fonte), mesmo bairro, mesmo tema, menos de 30 dias entre as aberturas e local igual pelo pseudônimo. Para isso, o encaminhamento passa a guardar também `id_local`, `numero_informado` e `servico_codigo` do registro, que nunca saem pela API. A plataforma mostra o mesmo problema:

- na fila e no detalhe do órgão, com a opção de **aplicar a mesma resposta** às ocorrências do mesmo problema do mesmo órgão (tudo ou nada, até 20);
- na lista e no detalhe dos encaminhamentos da gestão;
- antes de encaminhar, quando já há encaminhamento aberto para o mesmo problema;
- como contagem dos registros da base com o mesmo local, tema e fonte em até 30 dias.

**6. Avisos dentro da plataforma.** Cada perfil ganha notificações (`app.notificacao`), mostradas num sino no cabeçalho. O e-mail continua saindo como na ADR 0011, respeitando quem desligou os avisos:

| Quem | Quando |
|---|---|
| Pessoas do órgão | Chega uma ocorrência nova; o prazo de uma ocorrência aberta vence |
| Quem encaminhou, na gestão | O órgão responde |
| Cidadão que acompanha o protocolo ou que relatou | O pedido muda de etapa, com a resposta ao cidadão e a previsão |

As telas do ciclo consultam os encaminhamentos na hora e se recarregam quando chega uma notificação nova, então o fim de um atendimento aparece nos painéis do órgão, da gestão e do cidadão sem recarregar a página.

**7. Comparar os órgãos.** A tela "Órgãos" da gestão mostra, por órgão: encaminhados, abertos, vencidos, resolvidos, resolvidos no prazo, mediana de dias até resolver, devolvidos, acessos ativos e quantas resoluções **voltaram a ser pedidas**: o encaminhamento resolvido cujo local (mesma fonte, `id_local` e tema) ganhou um registro novo na base em até 30 dias depois da resolução.

## Consequências

- A migração 0010 cria `app.convite_de_acesso` e `app.notificacao`, acrescenta `orgao` à conta, a resposta ao cidadão e a previsão ao evento do encaminhamento, os campos de comparação ao encaminhamento (preenchidos a partir da base para os que já existiam), um índice parcial em `ouro.fato_demanda (id_local, categoria, data_abertura)` e a view `ouro.mv_demanda_por_orgao`.
- A conta de demonstração precisa ser do perfil Administração para mostrar o cadastro de acessos. O comando `recifeview mudar-perfil` troca o perfil de uma conta da gestão.
- Os órgãos são os do catálogo. Um órgão novo continua exigindo mudança de código.
- Os pesos da regra de mesmo problema seguem sem calibração, como na ADR 0009. "Voltou a ser pedido" só aparece para fontes com `id_local` (156 e formulário).
- Ficam em aberto: o provedor de e-mail, os canais reais de cada órgão e se o órgão deve ver o endereço exato quando houver acordo formal com a Prefeitura.
