# 0012. Trazer dados de um endereço na internet e de um banco externo, além do arquivo enviado

- **Status:** proposta
- **Data:** 11/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi pedida em 11/11/2026, depois do retorno dado ao protótipo no mesmo dia

## Contexto

Hoje os dados só entram por arquivo: enviado pelo painel ou apontado no terminal ([ADR 0007](0007-importacao-de-arquivos-pelo-painel.md)). O retorno de 11/11/2026 lembrou que, num uso real pela Prefeitura, os dados vêm de conector de banco, da nuvem e de outros sistemas, e que o produto precisa de mais de uma opção de entrada. O Processor, que faria a coleta agendada, ainda não existe, e duas decisões que ele depende seguem em aberto: onde guardar a camada bruta (S3 ou schema `raw`) e onde ele roda (Lambda ou Fargate).

A ADR 0007 dizia que a API não coleta dado externo: quem traz o arquivo é uma pessoa. Esta ADR muda isso de forma controlada.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Origens novas como portas que entregam um arquivo ao fluxo que já existe | Tudo continua passando pela mesma normalização, privacidade, pendências, histórico e desfazer. O Processor reaproveita os adaptadores | A API passa a abrir conexões para fora, só quando uma pessoa da gestão ou o agendador pede |
| Esperar o Processor para qualquer origem nova | Respeita o desenho original | Nada de novo para mostrar até o Processor existir |
| Conector que grava direto na base, sem o fluxo da importação | Mais rápido | Pularia pendências, privacidade, pente fino e desfazer |

## Decisão

Cada origem é uma porta que entrega um `ArquivoRecebido` ao mesmo fluxo da importação. Depois da entrega, nada muda: análise, colunas, pendências, pente fino, carga e desfazer.

| Origem | Porta | Implementação | Proteções |
|---|---|---|---|
| Arquivo do computador | `ArmazenamentoDeArquivos` | Já existia | Já existiam |
| Endereço na internet | `OrigemPorEndereco` | `urllib` da biblioteca padrão | Só `https`, só os hosts de `API_HOSTS_DE_IMPORTACAO` (padrão: `dados.recife.pe.gov.br`), mesmo tamanho máximo do envio, tempo limite |
| Banco externo | `OrigemPorBanco` | SQLAlchemy, com os drivers já instalados (PostgreSQL) | Conexões só por `API_BANCOS_DE_ORIGEM`, nunca digitadas na tela. Só `SELECT` ou `WITH`, um comando por vez, em transação só de leitura e com tempo limite. A tela mostra o nome da conexão, nunca a URL |
| Nuvem (S3) | Não criada | Nenhuma | Depende da decisão da camada bruta e de uma biblioteca nova (boto3) que o grupo não aprovou |

**Pela tela:** "Nova importação" passa a ter três abas: arquivo, endereço e banco. A aba de banco só aparece quando há conexão configurada.

**Pelo terminal:** `recifeview importar` aceita `--endereco` ou `--banco` com `--consulta`, além de `--arquivo`. É o caminho para o agendador rodar enquanto o Processor não existe.

**Privacidade:** a origem não muda as regras. Uma consulta que traga nome, CPF, contato ou endereço cai nas mesmas colunas bloqueadas da importação, e o texto da SEDEC continua descartado na leitura.

## Consequências

- A API pode abrir conexão para fora, mas só para os hosts e bancos que estão na configuração. Sem configuração, só o portal de dados abertos do Recife.
- O download acontece durante a requisição. Arquivos anuais grandes podem levar alguns minutos; para eles, o terminal é o caminho indicado.
- Um banco de outra tecnologia (Oracle, SQL Server) precisa do driver correspondente, que é dependência nova e passa pelo grupo.
- Quando o Processor existir, ele usa as mesmas portas. A escolha entre S3 e `raw` continua sendo a próxima implementação de `ArmazenamentoDeArquivos`.
- [arquitetura.md](../arquitetura.md) deixa de dizer que a API nunca coleta dado externo e passa a listar as origens.
