# 0010. Abrir contas de cidadão e separar três níveis de acesso

- **Status:** proposta
- **Data:** 10/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi pedida em 10/11/2026

## Contexto

Até aqui, só a gestão tinha conta, criada pela administração ([ADR 0005](0005-autenticacao-com-jwt-proprio.md)). O pedido é que qualquer pessoa possa criar uma conta para acompanhar os problemas relatados por outras pessoas e agir como fiscal da cidade, sem acesso ao que é da gestão. A página pública também passa a falar com essa pessoa, e não com a gestão.

Havia um risco antes de qualquer cadastro: as rotas do painel e da importação só conferiam se havia sessão, não o perfil. Abrir o cadastro sem mudar isso daria a qualquer conta nova o poder de importar dados.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Mesma tabela de usuários com o perfil `CIDADAO` e guarda por perfil nas rotas | Uma sessão, um login, uma auditoria. A regra fica num lugar só (`exigir_gestao`) | Toda rota nova da gestão precisa da guarda. Um teste lista as rotas e cobra o 403 |
| Sistema de contas separado para cidadãos | Isolamento total | Duas sessões, dois cadastros de senha, duas auditorias para manter |
| Mostrar os relatos sem conta | Nada a construir | Expõe rua e situação a robôs e a qualquer pessoa, e não atende o pedido |

## Decisão

Perfil `CIDADAO` na tabela `app.usuario`, com guarda por perfil. Três níveis de acesso:

| Nível | Vê |
|---|---|
| Sem conta | A página pública: números agregados dos dados abertos, indicadores do bairro comparados com o Recife, consulta de um pedido pelo protocolo, como funciona, privacidade e o formulário de relato |
| Cidadão | Também os relatos da cidade dos últimos 90 dias, os próprios relatos e os pedidos que guardou para acompanhar |
| Gestão | Tudo: painel, War Room, prioridade, pontos crônicos, pente fino com endereço completo e detalhe, importação |

**O que o cidadão vê de um relato:** serviço, tema, bairro, rua (só se ela estiver na lista oficial de vias), faixa de numeração de 100 em 100, data, quantas pessoas relataram, quantas disseram que não tiveram retorno e a situação (recebido, em análise, no painel da gestão, coberto por pedido oficial). Nunca vê o número exato, o texto escrito, o pseudônimo nem quem relatou. A faixa segue a mesma ideia do arredondamento das coordenadas para cerca de 100 m ([dados.md](../dados.md#privacidade-lgpd)). Rua fora da lista oficial some, para o campo de rua não virar mural de recado.

**Quem relatou continua oculto para a gestão:** quem relata não precisa entrar. Desde 10/11/2026, a pedido do grupo, o relato enviado com a conta de cidadão aberta fica ligado a ela (`contribuicao.usuario_id`) e aparece em "Meus relatos", com endereço, texto e o andamento (recebido, em análise, no painel da gestão ou já com pedido oficial). Só a própria pessoa vê essa lista. Nenhuma tela, rota ou pacote da gestão lê a coluna, e relato enviado sem conta ou por conta da gestão fica sem dono. Excluir a conta apaga nome e e-mail, e o relato passa a apontar para uma conta sem nada que identifique alguém. O endereço e o texto continuam apagados em 90 dias.

**Cadastro e proteções:**

- Pede nome, e-mail, senha e, se a pessoa quiser, o bairro. Não pede CPF nem telefone, porque nada no produto precisa deles.
- Sem confirmação por e-mail (mudança de 10/11/2026, a pedido do grupo, para simplificar): a conta nasce pronta e o cadastro já abre a sessão. Se o e-mail já tem conta, o cadastro diz isso no campo de e-mail. O custo: o cadastro revela quais e-mails têm conta, e alguém pode cadastrar o e-mail de outra pessoa. O dono recupera o acesso por "Esqueci minha senha", e a conta de cidadão só dá acesso a dados já anonimizados.
- A recuperação de senha responde sempre a mesma coisa, para não revelar se o e-mail tem conta. O código vale 15 minutos, aceita 5 tentativas e é guardado só como hash. Um código novo invalida o anterior, e só sai um por minuto.
- Limite de 10 operações de conta a cada 10 minutos por origem, campo-armadilha para robôs, aceite obrigatório e o bloqueio de 15 minutos depois de 5 senhas erradas, que já existia.
- Nova senha por código, só para contas de cidadão. A da gestão continua com a administração.
- Excluir a conta pede a senha, apaga nome, e-mail e bairro, derruba as sessões e mantém só a linha que a auditoria referencia.
- Pela porta da gestão (`area=gestao`), conta de cidadão recebe 403.
- Cada perfil tem só a sua área: a conta da gestão recebe 403 nas rotas `/cidade` e é levada ao painel se abrir a área do cidadão no navegador (10/11/2026, a pedido do grupo).

**E-mail:** só a recuperação de senha usa e-mail. O provedor de envio está em aberto. A porta `EnvioDeEmail` tem duas implementações: a local, que grava cada mensagem em `API_PASTA_DOS_EMAILS`, fora do git, e uma por SMTP genérico (`API_SMTP_*`), que serve para qualquer provedor (Gmail para teste, Amazon SES, Brevo, o servidor da Prefeitura). Sem `API_SMTP_SERVIDOR`, vale a local. Se o servidor recusar o envio, a operação é desfeita e a API responde 503. O que falta decidir é qual provedor e qual remetente o RecifeView usa de verdade.

**Visual:** a área do cidadão usa o cabeçalho em `azul-principal`, e a da gestão continua em `azul-marinho`. Os dois logins têm painéis de cores diferentes.

**Mudança de 11/11/2026 ([ADR 0011](0011-encaminhamento-ao-orgao-e-retorno.md)):** depois do retorno dado ao protótipo, o foco da área do cidadão passa a ser o acesso à informação. Os indicadores do bairro saem da conta e ficam públicos, a consulta pelo protocolo não pede conta, e a conta ganha "Meus pedidos": a pessoa guarda até 20 protocolos de pedidos feitos no Conecta Recife, no 156 ou na Ouvidoria e acompanha o andamento, incluindo para qual órgão a ocorrência foi encaminhada e o que ele respondeu. Os protocolos guardados são apagados com a conta.

## Consequências

- Toda rota nova da gestão precisa de `GestorAtualDep` ou de `exigir_gestao` no roteador. O teste `test_cidadao_recebe_403_em_toda_rota_da_gestao` lista as rotas e precisa crescer junto.
- Com contas abertas, o sistema passa a guardar dado pessoal de cidadãos (nome e e-mail). O grupo precisa revisar a base legal, o texto de privacidade e o prazo de guarda antes de publicar.
- O limite por origem vive na memória de um processo, como o do formulário (ADR 0009).
- O provedor de e-mail precisa ser escolhido antes de qualquer publicação, ou "Esqueci minha senha" não funciona fora da máquina de desenvolvimento.
- Se o grupo quiser a confirmação do e-mail de volta, ela depende do mesmo provedor.
