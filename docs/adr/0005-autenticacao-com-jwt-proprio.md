# 0005. Autenticar gestores com JWT próprio atrás de uma porta

- **Status:** proposta
- **Data:** 26/10/2026
- **Quem decidiu:** a decidir pelo grupo; a implementação local foi aprovada por Mateus Ribeiro para destravar o fluxo de login

## Contexto

O painel é só para gestores públicos, então precisa de login desde a primeira versão. A forma de autenticar está em aberto desde o C4 v0.1: JWT próprio ou um serviço gerenciado como o Amazon Cognito. O código não pode esperar essa decisão, e a regra do projeto é que decisão em aberto vira porta com implementação local ([clean-architecture.md](../clean-architecture.md)).

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| JWT próprio | Roda localmente sem nuvem; o grupo controla e entende cada parte; sem custo | O grupo mantém hash de senha, bloqueio e sessão |
| Amazon Cognito | Recuperação de senha por e-mail, MFA e políticas prontas | Exige conta AWS configurada; mais difícil de rodar e testar localmente |

## Como está implementado

- **Senha:** hash Argon2 (argon2-cffi). Mínimo de 12 caracteres, sem conter a parte do e-mail antes do @.
- **Bloqueio:** 5 tentativas erradas seguidas bloqueiam a conta por 15 minutos.
- **Token de acesso:** JWT HS256 de 15 minutos, guardado só na memória do navegador.
- **Sessão:** token aleatório num cookie `httpOnly`, `SameSite=Strict`, restrito ao caminho `/api/v1/autenticacao` e válido por 12 horas. O banco guarda só o hash SHA-256 dele, e sair ou trocar a senha revoga a sessão no servidor.
- **Sem rotação do token de sessão a cada renovação:** a rotação estrita derruba o gestor quando duas abas renovam ao mesmo tempo. A proteção que ela daria já vem do cookie `httpOnly` com `SameSite=Strict` e da revogação no servidor.
- **Contas:** criadas pela administração por linha de comando, com senha temporária que precisa ser trocada no primeiro acesso. Não há cadastro aberto nem recuperação por e-mail.
- **Auditoria:** entradas, recusas, bloqueios, saídas e trocas de senha ficam em `app.evento_de_acesso`, sem IP e sem o e-mail digitado.

As portas ficam em `backend/app/application/portas/`: `HashDeSenha`, `EmissorDeTokenDeAcesso`, `UsuarioRepository`, `SessaoRepository` e `RegistroDeAcessos`.

## Consequências

- Se o grupo aceitar esta proposta, ela vira "aceita" e o item sai das decisões em aberto.
- Se o grupo escolher o Cognito, mudam os adaptadores de `infrastructure/auth/` e as rotas de `api/routers/autenticacao.py` passam a delegar a ele. As telas e o contrato da API continuam os mesmos.
- O token de acesso continua válido até expirar (15 minutos) mesmo depois de sair. É o custo normal de um JWT sem consulta ao banco a cada requisição.
