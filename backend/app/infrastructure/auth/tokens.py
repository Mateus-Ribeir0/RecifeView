from datetime import datetime, timedelta
from uuid import UUID

import jwt

from app.application.portas.seguranca import TokenDeAcesso
from app.domain.erros import SessaoInvalida
from app.domain.usuario import Usuario

ALGORITMO = "HS256"
EMISSOR = "recifeview"


class EmissorDeTokenJwt:
    def __init__(self, segredo: str, duracao: timedelta) -> None:
        self._segredo = segredo
        self._duracao = duracao

    def emitir(self, usuario: Usuario, agora: datetime) -> TokenDeAcesso:
        expira_em = agora + self._duracao
        conteudo = {
            "sub": str(usuario.id),
            "iss": EMISSOR,
            "iat": int(agora.timestamp()),
            "exp": int(expira_em.timestamp()),
        }
        return TokenDeAcesso(jwt.encode(conteudo, self._segredo, algorithm=ALGORITMO), expira_em)

    def identificar(self, token: str, agora: datetime) -> UUID:
        try:
            conteudo = jwt.decode(
                token,
                self._segredo,
                algorithms=[ALGORITMO],
                issuer=EMISSOR,
                options={"verify_exp": False, "verify_iat": False, "require": ["sub", "exp"]},
            )
            if agora.timestamp() >= conteudo["exp"]:
                raise SessaoInvalida
            return UUID(conteudo["sub"])
        except (jwt.InvalidTokenError, ValueError) as erro:
            raise SessaoInvalida from erro
