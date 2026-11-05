# 0007. Importar arquivos pelo painel, com a normalização no backend

- **Status:** proposta
- **Data:** 05/11/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi aprovada por Mateus Ribeiro

## Contexto

Gestores precisam trazer arquivos novos (uma nova versão anual do 156, por exemplo) sem depender de quem roda scripts. [arquitetura.md](../arquitetura.md#c2--containers) diz que a API não coleta dado externo e que o Processor faz a carga, mas o Processor ainda não existe, e a coleta agendada não cobre um arquivo que alguém tem em mãos. Arquivos reais trazem colunas diferentes, grafias diferentes e às vezes dado pessoal, então a carga precisa perguntar em vez de adivinhar.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Normalização no backend, atrás de portas | Funciona hoje; um deploy só; regras testáveis no domínio | A API ganha um trabalho de ingestão que o desenho original dava ao Processor |
| API guarda o arquivo e o Processor normaliza | Respeita o desenho original | Exige criar o Processor e uma fila antes de qualquer tela |
| Scripts manuais, sem tela | Nada a construir | Não atende quem usa o painel; sem histórico nem decisões registradas |

## Decisão

Receber o arquivo pela API e normalizar no backend, com regras puras em `domain/importacao` e toda entrada e saída atrás de portas. Assim o trabalho pode migrar para o Processor mudando adaptadores.

- **Decisão humana antes da carga:** coluna que não bate, valor desconhecido, data ambígua e registro repetido viram pendências. Nada entra enquanto houver pendência aberta. As escolhas ficam guardadas na importação.
- **Permissão:** todo gestor autenticado importa e desfaz. Tudo fica no histórico com autoria.
- **Desfazer:** a versão anterior das linhas atualizadas fica em `ouro.fato_demanda_substituida`. Só a importação mais recente pode ser desfeita, porque uma mais nova pode ter atualizado as mesmas linhas.
- **Camada bruta:** continua em aberto entre S3 e schema `raw`. A porta `ArmazenamentoDeArquivos` tem só a versão local, numa pasta fora do git.
- **Processamento:** a porta `FilaDeImportacoes` tem só a versão em processo, com uma tarefa por vez.
- **Formatos:** CSV, TSV, JSON, XLSX, ZIP, GZ e XZ. O XLSX usa a biblioteca openpyxl.

**Privacidade:**

- Colunas de nome, CPF, telefone, e-mail e endereço são reconhecidas pelo nome e pelo conteúdo, ficam bloqueadas no mapeamento e os valores nunca são exibidos, registrados em log ou guardados no histórico.
- O texto da SEDEC é descartado na leitura.
- Arquivo com dado pessoal não fica guardado depois da carga: só o resultado tratado permanece.
- A API nunca devolve o arquivo original.
- `id_local` usa o sal de `API_SAL_DO_ID_LOCAL`. Sem o sal, os registros novos entram sem `id_local` e ficam fora da reincidência, e a tela avisa.

## Consequências

- A regra "a API não coleta dado externo" continua valendo: quem traz o arquivo é uma pessoa autenticada. [arquitetura.md](../arquitetura.md) passa a descrever esse caminho.
- Um arquivo grande ocupa a fila por alguns minutos. Se o volume crescer, o trabalho vai para o Processor.
- Layouts conhecidos: dataset do grupo, 156, Ouvidoria e Defesa Civil do Portal. A Câmara vem de coleta própria, com a tramitação em arquivo separado, então entra pelo dataset ou por mapeamento manual.
