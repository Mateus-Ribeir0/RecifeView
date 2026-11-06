# 0009. Receber relatos por um formulário público e conferir duplicidade entre canais

- **Status:** proposta
- **Data:** 06/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi pedida em 06/11/2026, junto com a nova página pública

## Contexto

A página pública ganhou um formulário para qualquer pessoa relatar um problema urbano. Os relatos precisam virar um pacote que entra no painel, sem que a mesma demanda conte duas vezes. Isso acontece de três jeitos:

1. Duas pessoas relatam o mesmo problema pelo formulário.
2. A gestão importa um arquivo (do 156, por exemplo) com uma demanda que alguém também relatou no formulário.
3. Um pacote de relatos chega à base depois de o mesmo pedido já ter entrado por um arquivo oficial.

Três fatos dos dados limitam a solução. As fontes não têm chave em comum ([dados.md](../dados.md#cuidados-antes-de-usar)). A base analítica não guarda endereço nem texto: só `id_local`, um hash. E a repetição é justamente o que o painel quer medir: 64,4% dos intervalos entre pedidos no mesmo local e serviço são de 30 dias ou mais, ou seja, reincidência. Apagar repetição sem critério destruiria o indicador.

A mudança também mexe no escopo: [contexto.md](../contexto.md#o-problema) diz que o RecifeView não faz triagem do lado do cidadão. O formulário não faz triagem nem atendimento: ele só alimenta a análise, e isso está escrito para quem preenche. O grupo precisa confirmar se aceita essa ampliação.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Vinculação de registros em camadas: bloqueio por bairro e tema, regras de tempo e semelhança por trigramas | Roda com a biblioteca padrão, sem dependência nova. Cada apontamento tem motivo legível. Usa as regras que o projeto já tem (7 e 30 dias). Compara o que existe dos dois lados | Não entende sinônimo. Os pesos foram definidos à mão |
| Busca vetorial com embeddings (pgvector e um modelo de linguagem) | Entende que "cratera" e "buraco" são parecidos | O `pgvector` não está disponível e o 156, a Ouvidoria e a Defesa Civil não têm texto na base, então não haveria o que comparar entre canais. Modelo local ocupa disco; serviço externo mandaria texto do cidadão para fora. A nota não se explica ao gestor |
| Só hash exato | Trivial | "R. do Sol" e "Rua do Sol" virariam duas ocorrências |
| Um modelo de linguagem julgando cada par | Flexível | Custo por par, texto saindo da plataforma, resultado que muda entre execuções |

## Decisão

Adotar a vinculação de registros em camadas, nesta ordem, com regras puras em `domain/contribuicao`.

**Fluxo:** o relato entra em `app.contribuicao`, uma quarentena fora da base analítica. A gestão revisa em `/painel/contribuicoes` e gera um pacote, que é um arquivo que segue o fluxo normal da importação ([ADR 0007](0007-importacao-de-arquivos-pelo-painel.md)), com histórico e desfazer. Na base, o relato vira a sexta fonte, `FORMULARIO_PUBLICO`. Ela fica fora das views do 156, então 53,3% e os prazos não mudam.

**Camadas do pente fino:**

| Camada | O que faz | Resultado |
|---|---|---|
| 1. Chave de envio | Cada formulário tem uma chave única | Reenvio e clique duplo não contam de novo |
| 2. Endereço canônico | Reescreve a via como a Central 156 escreve (`R.` vira `RUA`, `1ª Travessa` vira `1TR`) e reconhece a via na lista do bairro | O mesmo `id_local` do arquivo oficial, quando há sal |
| 3. Bloqueio | Só compara dentro do mesmo bairro e categoria | Evita comparar o que não pode ser igual |
| 4. Regra do tempo | Até 7 dias é duplicidade, 8 a 29 vai para revisão, 30 ou mais é reincidência (`docs/dados.md`) | Reincidência nunca é tratada como duplicata |
| 5. Pontuação | Local 60%, serviço 20%, tempo 15%, detalhe 5%. Trigramas com coeficiente de Dice | A partir de 0,72, a dupla vai para revisão |
| 6. Decisão humana | Só soma sozinho com endereço igual, número informado, mesmo serviço e até 7 dias | O resto espera uma pessoa |

**Importação:** toda importação passa pelo pente fino. Arquivo manual é comparado com os relatos, usando o endereço só durante a leitura. Pacote é comparado com a base pelo `id_local`. Coincidência vira as pendências `coincidencias_certas` e `coincidencias_provaveis`, e a carga fica travada até a decisão. Manter o registro oficial tira o relato da base pela mesma tabela do desfazer (`fato_demanda_substituida`).

**Privacidade:**

- O formulário não pede identificação e recusa CPF, telefone e e-mail no texto.
- Endereço e detalhe ficam só em `app.contribuicao`, são vistos apenas pela gestão autenticada, com auditoria, e são apagados em 90 dias, por uma tarefa que roda a cada 6 horas dentro da API. O prazo cobre a espera até o arquivo oficial ser publicado.
- O pacote, a base analítica e o histórico de importações não recebem endereço nem texto.
- Esse é o primeiro dado que o sistema recebe direto do público. O grupo precisa revisar a base legal e o aviso antes de publicar.

**Proteção da rota pública:** limite de envios por origem na memória do processo (porta `LimiteDeEnvios`) e campo-armadilha para robôs. Nenhum relato chega ao painel sem revisão, então spam não contamina indicador.

**Lista de vias:** `ouro.dim_logradouro` guarda os nomes de via dos arquivos públicos do 156, carregados com `recifeview carregar-logradouros`. Só entra via com pelo menos 2 pedidos.

## Medição

O limite de reconhecimento de via saiu de uma varredura com as vias reais do arquivo público de 2025 da Central 156 (7.507 pares de bairro e via depois do filtro; 3.000 variantes geradas por tipo). A medição é reproduzível, mas as variantes são sintéticas.

| Limite | Via digitada com um erro: acerto | Rua de fora confundida com rua do bairro |
|---|---|---|
| 0,55 | 96,1% | 3,28% |
| 0,60 | 94,7% | 1,94% |
| **0,65 (escolhido)** | **89,8%** | **0,69%** |
| 0,70 | 83,8% | 0,45% |
| 0,82 | 44,0% | 0,07% |

Com 0,65, variações de prefixo e título foram reconhecidas em 100% dos casos, e via omitida do tipo (só "Flores") em 86%, porque empate não escolhe nenhuma via. Entre vias diferentes do mesmo bairro, o percentil 99,9 da semelhança é 0,60.

## Consequências

- Os pesos e o limite de 0,72 **não foram calibrados com dados rotulados**, porque ainda não existem. Cada decisão da gestão fica em `app.par_de_contribuicoes` e serve para essa calibração.
- Sem o sal (`API_SAL_DO_ID_LOCAL`), o pacote não consegue se comparar com a base, porque ela só guarda o hash. Os relatos ficam contados como "sem comparação de endereço" e a tela avisa.
- Arquivo sem coluna de endereço também não é comparável. Uma comparação só por bairro, serviço e data daria falso positivo demais num bairro movimentado.
- Depois de 90 dias, o relato só é comparável pelo `id_local`.
- Sinônimos não são tratados. O formulário reduz esse risco porque o serviço é escolhido numa lista, e não digitado. Se o texto livre ganhar peso, a busca vetorial pode entrar atrás da mesma comparação, com um modelo local.
- A comparação entre duas fontes oficiais continua fora do escopo, porque elas não têm endereço comparável em comum na base.
- Uma pessoa que recarrega a página e envia de novo gera outra chave e conta como mais um relato. O sistema não identifica pessoas de propósito.
- O limite de envios vive na memória de um processo e usa o endereço da conexão. Com mais de uma instância da API ou atrás de um proxy, ele precisa de outra implementação da porta.
