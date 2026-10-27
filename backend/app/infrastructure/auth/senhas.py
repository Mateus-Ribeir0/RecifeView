import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError


class HashDeSenhaArgon2:
    def __init__(self) -> None:
        self._argon2 = PasswordHasher()
        self._hash_de_referencia = self._argon2.hash(secrets.token_urlsafe(16))

    def gerar(self, senha: str) -> str:
        return self._argon2.hash(senha)

    def confere(self, senha: str, hash_da_senha: str) -> bool:
        try:
            return self._argon2.verify(hash_da_senha, senha)
        except (VerificationError, InvalidHashError):
            return False

    def simular_conferencia(self, senha: str) -> None:
        self.confere(senha, self._hash_de_referencia)
