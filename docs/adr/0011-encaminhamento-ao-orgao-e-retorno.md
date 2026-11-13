# 0011. Encaminhar a ocorrência priorizada ao órgão responsável e devolver o andamento a quem pediu

- **Status:** proposta
- **Data:** 11/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi pedida em 11/11/2026, depois do retorno dado ao protótipo no mesmo dia

## Contexto

O retorno de 11/11/2026 sobre o protótipo apontou três coisas:

1. O problema do desafio é B2G, do lado de dentro da Prefeitura. Quem recebe a denúncia é o Conecta Recife, a Central 156 e os canais dos próprios órgãos. O RecifeView não deve refazer isso.
2. Falta a decisão que vem depois da prioridade: para onde a ocorrência priorizada vai, de novo, e como ela chega lá. Emlurb, Compesa, Neoenergia e CTTU têm canais próprios de ocorrência. A sugestão foi automatizar o envio quando a ocorrência for priorizada, até com um robô que preencha o canal do órgão.
3. O cidadão não precisa de mais um lugar para registrar, e sim de acesso à informação: consultar o andamento do pedido que ele já fez, pelo protocolo.

O painel já classifica as ocorrências abertas (fila da tela Prioridade), mas a fila termina na tela: não há como mandar uma ocorrência a um órgão, saber se ele recebeu nem contar isso a quem pediu. O ciclo fica aberto justamente na etapa que a pergunta central do projeto quer medir, entre o canal e o órgão.

Fatos dos dados que limitam a solução:

- A base aberta do 156 não traz protocolo. A da Ouvidoria traz (`NO_PROTOCOLO`), mas a importação descartava a coluna.
- A base analítica não guarda endereço ([dados.md](../dados.md#privacidade-lgpd)). O encaminhamento não tem como mandar o endereço de um registro oficial.
- O órgão de destino aparece de forma diferente em cada fonte: fixo como Emlurb no 156, inferido por palavra-chave na Câmara (rótulo fraco), por secretaria na Ouvidoria.

## Opções consideradas

**Como sugerir o órgão de destino**

| Opção | A favor | Contra |
|---|---|---|
| Regra explicável a partir dos dados: o órgão que o próprio registro aponta; sem isso, o órgão mais citado nas indicações da Câmara do mesmo tema | Cada sugestão tem motivo e número que se conferem numa consulta. Não depende de modelo treinado | O órgão da Câmara é rótulo fraco. Para o 156 a sugestão quase sempre repete a Emlurb |
| Classificador treinado (proposta de Gustavo para a priorização) | Pode aprender casos que a regra não vê | Ainda não existe; sem rótulo de destino correto para treinar e medir |
| Tabela de-para escrita pelo grupo | Simples | Seria uma afirmação sobre competência dos órgãos sem fonte. Envelhece sem ninguém perceber |

**Como entregar ao órgão**

| Opção | A favor | Contra |
|---|---|---|
| Porta de envio com três canais: caixa de saída local, e-mail e webhook | Cobre órgão sem sistema (e-mail) e com sistema (webhook). Configurável por órgão, sem mudar código | E-mail depende do provedor, que segue em aberto ([ADR 0010](0010-contas-de-cidadao-e-niveis-de-acesso.md)) |
| Robô que entra no site do órgão com uma senha e preenche o formulário de ocorrência | Usa o canal que o órgão já atende | Quebra quando o site muda; esbarra em captcha e em termos de uso; usa a senha de uma pessoa; registra em nome de quem não pediu. Fica como implementação futura da mesma porta, se um órgão autorizar |
| Integração direta com o sistema de cada órgão | A mais robusta | Depende de acordo com cada órgão; nenhum foi feito |

**Como o órgão responde**

| Opção | A favor | Contra |
|---|---|---|
| Link de retorno único em cada mensagem, sem login, que serve também de API | Órgão não precisa de conta. Pessoa e sistema usam o mesmo endereço. O link só vale para aquele encaminhamento | Quem tiver o link responde. Mitigado: o token é longo, guardado só como hash, vence e só aceita a resposta seguinte do ciclo |
| Conta para cada órgão no RecifeView | Autenticação forte | Mais um cadastro e mais senhas para órgãos externos |
| Só a gestão registra o que ouviu do órgão | Nada a construir no lado do órgão | O ciclo depende de alguém lembrar de registrar |

## Decisão

Fechar o ciclo em quatro passos, com regras puras em `domain/encaminhamento` e toda entrada e saída atrás de portas.

**1. Sugestão de destino.** Para cada ocorrência da fila, a API sugere um órgão do catálogo (Emlurb, Compesa, Neoenergia, CTTU, Defesa Civil, Seinfra, URB, Saúde, Meio Ambiente e Ordem Pública, os mesmos que aparecem nas indicações da Câmara):

1. O órgão que o próprio registro aponta, quando ele está no catálogo.
2. Senão, o órgão mais citado nas indicações da Câmara do mesmo tema (`ouro.mv_camara_indicacoes`, 2021 a 2025). As categorias do 156 que a Câmara não usa entram pelo tema mais próximo (luminárias e postes em iluminação, macrodrenagem em drenagem).
3. Senão, nenhuma sugestão: o gestor escolhe.

A tela mostra sempre a distribuição do tema como evidência. Exemplo da base local de 11/11/2026: nas 8.925 indicações de drenagem, 87,4% citam a Emlurb, 9,2% a Seinfra e 0,2% a Compesa. A gestão confirma ou troca o órgão; a sugestão nunca envia nada sozinha pela tela. O classificador, quando existir, entra atrás da mesma regra.

**2. Envio.** Encaminhar grava `app.encaminhamento` com uma cópia do que foi mandado (fonte, data, tema, serviço, bairro, situação, protocolo de origem e nota da fila) e despacha a mensagem pela porta `DespachoAosOrgaos`. O canal de cada órgão vem de `API_CANAIS_DOS_ORGAOS`:

- `local`: grava a mensagem em `API_PASTA_DOS_ENCAMINHAMENTOS`, fora do git. É o padrão de todo órgão sem canal configurado.
- `email`: manda pela mesma porta `EnvioDeEmail` das contas (SMTP ou caixa local).
- `webhook`: faz `POST` do JSON do encaminhamento no endereço do órgão, com token opcional.

Se o canal falhar, o encaminhamento fica como `falhou` e pode ser reenviado. Uma ocorrência não tem dois encaminhamentos abertos ao mesmo tempo. Depois de devolvida ou de uma falha, ela pode seguir para outro órgão.

**Envio automático:** o comando `recifeview encaminhar-prioritarias` encaminha as ocorrências da fila com nota a partir de 7 (a mesma "nota alta" da tela), sem encaminhamento aberto e com sugestão de destino, até um limite por execução. Ele existe para o agendador (cron ou EventBridge) rodar; a tela continua pedindo confirmação.

**3. Retorno do órgão.** Cada mensagem leva um link `/retorno/<token>` (token aleatório de 32 bytes, guardado como hash SHA-256, válido por 60 dias). Pelo link, o órgão vê o que recebeu e marca `recebido`, `resolvido` ou `devolvido` (não é com ele), com o protocolo dele e uma observação curta. Um sistema usa o mesmo endereço com `POST` em JSON. A gestão também pode registrar o retorno pela tela. As transições permitidas são: enviado para recebido, resolvido ou devolvido; recebido para resolvido ou devolvido; falhou para enviado (reenvio). Resolvido e devolvido encerram o ciclo.

**Prazo:** o órgão tem 30 dias para resolver ou devolver, o prazo de resposta da Lei 13.460/2017 (art. 16). Depois disso o encaminhamento aparece como atrasado na tela Encaminhamentos.

**4. Retorno a quem pediu.** O protocolo passa a ser guardado em `ouro.fato_demanda.protocolo` quando a fonte o traz (hoje, o arquivo da Ouvidoria; no futuro, o conector da Prefeitura). Com ele:

- **Sem conta:** a página pública "Acompanhar um pedido" consulta pelo protocolo e mostra situação, órgão, prazos e, se houver, para quem a ocorrência foi encaminhada e o que o órgão respondeu.
- **Com conta de cidadão:** "Meus pedidos" guarda até 20 protocolos e mostra o andamento de todos juntos. "Meus relatos", do formulário, continua como estava.
- Os números do bairro, que eram só da conta, passam a ser públicos: são agregados dos dados abertos.

**5. Avisos às partes (revisão de 13/11/2026).** Na primeira versão, cada parte só ficava sabendo de uma mudança se abrisse a tela. Agora o próprio ciclo avisa, pela porta `EnvioDeEmail` das contas (SMTP, ou arquivos em `API_PASTA_DOS_EMAILS` enquanto o provedor segue em aberto):

| Quando | Quem é avisado | Como |
|---|---|---|
| O órgão responde pelo link (recebeu, resolveu, devolveu) | A pessoa da gestão que encaminhou | E-mail com o código, a resposta e o link do detalhe. No envio automático não há autor: vale o contador do menu |
| O prazo de 30 dias vence sem resolução nem devolução | O órgão | Lembrete pelo mesmo canal do envio, com um link novo que substitui o anterior. Um lembrete por encaminhamento, pelo comando `recifeview lembrar-orgaos`, feito para o agendador |
| O encaminhamento é enviado, recebido, resolvido ou devolvido | O cidadão com conta que guardou o protocolo em "Meus pedidos" ou que enviou um relato somado à ocorrência | E-mail com a etapa, o órgão e o link da própria área. Sem endereço, sem texto e sem a justificativa da gestão. A pessoa desliga em "Minha conta" |
| Há devolução sem novo destino, falha de envio, prazo vencido ou dupla esperando o pente fino | A gestão, dentro do painel | Contador no menu e filtro "Precisam de ação" na tela Encaminhamentos |

Quem pede sem conta não deixa contato, de propósito: acompanha pela consulta pública. A falha de um aviso não desfaz a mudança que o motivou; ela fica no log.

**6. O relato do formulário também chega ao órgão.** A ocorrência do formulário que já entrou na base pode ser encaminhada pela tela Contribuições. Como a base não guarda endereço, a mensagem leva a rua (só se estiver na lista oficial de vias) e a faixa de numeração de 100 em 100, o mesmo nível de detalhe que outras contas de cidadão já veem ([ADR 0010](0010-contas-de-cidadao-e-niveis-de-acesso.md)). O número exato e o texto continuam só com a gestão. "Meus relatos" mostra para qual órgão a ocorrência foi e em que etapa está.

**Privacidade:**

- O protocolo é um identificador publicado pela própria fonte (a Ouvidoria publica junto com assunto, órgão e situação). Ele só é devolvido em busca exata; nenhuma rota lista protocolos, e ele não vai para log.
- A consulta pública não devolve endereço, texto, `id_local` nem pseudônimo. O texto da SEDEC continua sem rota.
- A mensagem ao órgão não leva endereço nem texto, porque a base não os guarda. Leva o protocolo de origem, para o órgão achar o pedido no canal de onde ele veio.
- A observação do órgão e a justificativa da gestão recusam CPF, telefone e e-mail e têm até 280 caracteres.
- Protocolo guardado na conta é apagado com a conta.

## Consequências

- Os avisos por e-mail dependem do provedor de e-mail, que segue em aberto. Sem ele, os avisos ficam em arquivos e só servem para conferir o fluxo na máquina de desenvolvimento.
- O lembrete troca o link do órgão. Quem guardou o e-mail antigo passa a usar o do lembrete; a mensagem diz isso.

- O fluxo do produto passa a ser: entrada (importação ou conector), processamento (normalização e pente fino), priorização (fila), decisão e envio (encaminhamento), retorno do órgão e acesso à informação.
- A consulta pelo protocolo só acha pedidos de fontes que publicam protocolo. Com os arquivos abertos, isso vale para a Ouvidoria, e só depois de importar o arquivo dela pelo painel (o dataset do Drive não tem a coluna). Para o 156 depende do conector da Prefeitura ou do pedido LAI ao SGDE. A tela diz isso.
- Sem endereço na mensagem, o órgão depende do protocolo de origem para agir. Com um conector da Prefeitura, o endereço pode ir na mensagem, lido na hora e não guardado, como já acontece na leitura do pente fino.
- A sugestão herda a fraqueza do órgão inferido na Câmara. Cada decisão da gestão fica guardada com o órgão sugerido e o escolhido, e serve para medir a regra ou treinar o classificador.
- O link de retorno e a consulta pública são rotas sem sessão. Elas têm limite por origem na memória do processo, como o formulário ([ADR 0009](0009-formulario-publico-e-pente-fino.md)), e precisam de outra implementação da porta com mais de uma instância da API.
- O endereço público usado no link vem de `API_ENDERECO_DO_SITE`.
- Os canais reais de cada órgão (e-mail ou endereço do webhook) dependem de acordo com cada um. Até lá, tudo fica na caixa de saída local.
