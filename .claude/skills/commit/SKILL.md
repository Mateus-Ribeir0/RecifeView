---
name: commit
description: Faz commits no repositório do RecifeView seguindo o padrão do grupo (Conventional Commits em português, um assunto por commit, branch de trabalho, checagem de privacidade e de documentação). Use sempre que for commitar, ao concluir uma unidade de trabalho, quando pedirem "commita", "salva no git", "faz o commit" ou "organiza os commits", e antes de abrir um pull request.
---

# Commit no RecifeView

A regra completa está em `CONTRIBUTING.md`, seção "Commits". Este é o procedimento.

## 1. Veja o que mudou

```bash
git status
git diff
git diff --staged
git branch --show-current
```

Se a branch atual for `main`, crie uma de trabalho antes de commitar: `git switch -c tipo/descricao-curta` (ex.: `feat/mapa-coropletico-bairros`).

## 2. Barre o que não pode entrar

Pare e avise, sem commitar, se o diff tiver:

- Arquivo de dados: `.csv`, `.xz`, `.zip`, `.parquet`, `.ipynb` com saída de dados, dump de banco, qualquer coisa dentro de `data/`.
- `.env` real, `.salt_id_local`, token, senha, chave de API ou URL de banco com credencial.
- Texto da SEDEC em qualquer forma: fixture, teste, log, captura de tela, exemplo de documentação.
- Dado pessoal em claro.
- Link de pasta ou arquivo do Google Drive, número de protocolo ou e-mail de integrante. O repositório é público.

Se algo assim já tiver sido commitado antes, avise e não tente reescrever o histórico por conta própria.

## 3. Confira a documentação

Se a mudança instalou ou removeu dependência, criou variável de ambiente, comando, porta, pasta, rota ou passo de configuração, o README correspondente precisa mudar **no mesmo commit**. Se não mudou, rode a skill `atualizar-docs` antes de continuar.

## 4. Separe em commits atômicos

Agrupe as mudanças por assunto. Cada commit precisa fazer sentido sozinho e deixar o projeto funcionando.

- Dependência nova: um commit `build` com o manifesto e o lockfile, separado da funcionalidade que a usa.
- Formatação ou ordem de imports: commit `style` próprio, nunca misturado com mudança de comportamento.
- Migração de banco: commit `feat(db)` antes da rota que usa a tabela.
- Teste de uma correção: no mesmo commit do `fix`.
- README de uma funcionalidade: no mesmo commit da funcionalidade.

Adicione por caminho explícito (`git add frontend/src/map/ frontend/README.md`). Não use `git add -A` sem antes conferir o `git status`, e não use `git add -p` (o modo interativo não funciona aqui).

## 5. Rode as verificações

- Se o diff tem código, passe pela checagem final da skill `codigo-limpo` (camada, regra da dependência, nomes, comentários).
- Procure travessão e meia-risca no que vai entrar. Se aparecer algo, troque por vírgula, dois-pontos, parênteses ou "a":

```bash
git diff --staged | grep -nE '^\+.*[—–]'
```

- Se a parte alterada já tiver lint, formatação, checagem de tipos ou testes configurados (veja o README da pasta), rode tudo. Se falhar, corrija ou avise. Nunca use `--no-verify`.

## 6. Escreva a mensagem

```
tipo(escopo): descrição no imperativo, minúscula, sem ponto final

Corpo opcional: por que a mudança foi feita, em linhas de até 72
caracteres. Cite o achado, a ADR ou a seção de docs/dados.md quando
a mudança vier de uma delas.
```

- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Escopos: `frontend`, `backend`, `processor`, `db`, `infra`, `adr`, `repo`. Documentação geral vai sem escopo.
- Primeira linha com até 72 caracteres. Verbo como em "este commit adiciona": `adiciona`, `corrige`, `remove`, `extrai`, `atualiza`.
- Diga o efeito, não o arquivo: `feat(frontend): adiciona legenda por quantis ao mapa`, não `altera MapaBairros.tsx`.
- Sem emoji e sem travessão (— ou –).
- Se o ambiente pedir uma linha de coautoria, ela vai no rodapé, depois de uma linha em branco.

Use heredoc para preservar as quebras de linha:

```bash
git commit -F - <<'EOF'
feat(backend): adiciona rota de prazos por serviço

Devolve mediana e p90 de dias_ate_movimento, excluindo valores
negativos (defeito da fonte, ver docs/dados.md).
EOF
```

## 7. Se o commit falhar por identidade

Se o git responder "Please tell me who you are", **não configure nome nem e-mail por conta própria**. Avise a pessoa e mostre o comando para ela rodar no repositório:

```bash
git config user.name "Nome"
git config user.email "email@exemplo.com"
```

## 8. Confira e relate

```bash
git log --oneline -n 10
git status
```

Relate os commits criados (hash curto e mensagem) e o que ficou de fora, se algo ficou. Não faça push nem abra PR sem a pessoa pedir.
