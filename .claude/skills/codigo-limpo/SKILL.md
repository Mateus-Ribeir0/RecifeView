---
name: codigo-limpo
description: Escreve e revisa código do RecifeView seguindo a Clean Architecture e o Clean Code do grupo. Cobre as camadas domain, application, infrastructure e entrada; a regra da dependência; funções pequenas; nomes que dispensam comentário; comentário só quando indispensável; nenhum travessão. Use antes de criar ou alterar qualquer arquivo de código em frontend/, backend/ ou processor/, ao revisar um PR, e quando pedirem "refatora", "limpa esse código", "organiza as camadas" ou "revisa o código".
---

# Código limpo no RecifeView

As referências completas são [docs/clean-architecture.md](../../../docs/clean-architecture.md) (onde cada coisa mora) e [docs/padroes-de-codigo.md](../../../docs/padroes-de-codigo.md) (como escrever). Leia os dois antes da primeira mudança de código da sessão.

## 1. Antes de escrever: em que camada isso mora?

| O código... | Camada | Exemplo |
|---|---|---|
| Expressa uma regra do negócio, sem entrada nem saída | `domain` | Percentil com prazo negativo excluído, limiar de 1.000 moradores, quantis do mapa |
| Orquestra uma pergunta que o sistema responde | `application` (caso de uso) | `listar_prazos_por_servico`, `executar_carga`, `useDemandaPorBairro` |
| Descreve uma dependência externa que o caso de uso precisa | `application/portas` | `PrazoRepository`, `ArmazenamentoBruto`, `Extrator` |
| Fala com banco, rede, arquivo, nuvem ou biblioteca de gráfico e mapa | `infrastructure` (ou `ui/charts` e `ui/map` no frontend) | Repositório SQLAlchemy, extrator do SAGL, cliente HTTP |
| Recebe o mundo externo e monta as peças | Entrada | Router FastAPI, `handler.py`, páginas React, `main.py` |

Se a resposta for "um pouco de cada", o código precisa ser dividido.

## 2. Regra da dependência

Confira as importações do arquivo:

- `domain` só importa a biblioteca padrão (e o pandas no Processor).
- `application` importa `domain`. Nunca FastAPI, SQLAlchemy, boto3, httpx, React Query nem `fetch`.
- `infrastructure` implementa as portas de `application`.
- Só o ponto de montagem (`main.py`, `handler.py`, provedores em `ui/app`) conhece as implementações concretas.
- No frontend: Recharts só em `ui/charts`, Leaflet só em `ui/map`, `fetch` só em `infrastructure/api`. `domain` não importa React.

Uma decisão em aberto (S3 ou `raw`, Lambda ou Fargate, JWT ou Cognito) nunca entra no código como escolha feita. Implemente a porta e a versão local, e pare aí.

## 3. Enquanto escreve

- O nome diz o que é. Função é verbo, booleano é pergunta, sem abreviação inventada.
- Uma função faz uma coisa: até umas 20 linhas, no máximo 3 parâmetros, sem flag booleana.
- Guarda e retorno antecipado, no máximo 2 níveis de indentação.
- Constante nomeada no domínio em vez de número mágico. `Enum` ou union de literais em vez de string mágica.
- Exceção com nome do domínio em vez de `None` ou código de erro. Nada de `except: pass`.
- Lista vazia em vez de `None` quando o retorno é uma coleção.
- Não duplique regra de negócio, mas só extraia abstração na terceira repetição.

## 4. Comentário: precisa mesmo?

Por padrão, não. Antes de comentar, tente nesta ordem:

1. Renomear.
2. Extrair uma função com nome descritivo.
3. Extrair uma constante com nome descritivo.
4. Escrever um teste que mostre o comportamento.

Só comente se, depois disso, um leitor ainda fosse achar que o código está errado sem saber o porquê. O caso típico é um defeito da fonte de dados ou uma decisão contraintuitiva. Nesse caso, uma linha, com o porquê e o link para a seção de `docs/dados.md` ou para a ADR.

Remova sempre: comentário que repete o código, código comentado, `TODO` sem issue, divisória de seção e docstring que repete a assinatura.

## 5. Travessão

Nada que faça parte da aplicação tem travessão (—) nem meia-risca (–): texto de interface, strings, mensagens de erro, logs, comentários, commits e docs. Use vírgula, dois-pontos, parênteses, ponto ou "a" em intervalos (`2021 a 2025`).

```bash
grep -rnE '[—–]' frontend/src backend/app processor/recifeview_processor 2>/dev/null
git diff --staged | grep -nE '^\+.*[—–]'
```

## 6. Testes

- Regra nova no domínio: teste unitário sem entrada nem saída.
- Caso de uso novo: teste com implementação falsa das portas.
- Repositório ou extrator novo: teste de integração (PostgreSQL local, resposta HTTP gravada).
- Bug corrigido: teste de regressão.
- Fixture sintética e pequena. Nunca dado real, nunca texto da SEDEC.

## 7. Checagem final

Responda antes de dar como pronto. Qualquer "não" precisa ser corrigido.

- [ ] Cada arquivo novo está na camada certa e as importações respeitam a regra da dependência?
- [ ] Os nomes dispensam comentário?
- [ ] As funções são curtas, fazem uma coisa e têm até 3 parâmetros?
- [ ] Os comentários que sobraram são indispensáveis?
- [ ] Não há travessão nem meia-risca no diff?
- [ ] Não há código morto, `print` ou `console.log` esquecido?
- [ ] Toda regra nova tem teste na camada certa?
- [ ] Lint, formatação, tipos e testes passam?

Depois, siga para a skill `atualizar-docs` (se mudou a forma de rodar) e para a skill `commit`.
