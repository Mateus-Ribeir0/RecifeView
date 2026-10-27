import re
from dataclasses import dataclass

from app.domain.erros import EmailInvalido

TAMANHO_MAXIMO_DO_EMAIL = 254
_FORMATO_DE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    endereco: str

    def __post_init__(self) -> None:
        normalizado = self.endereco.strip().lower()
        if len(normalizado) > TAMANHO_MAXIMO_DO_EMAIL or not _FORMATO_DE_EMAIL.match(normalizado):
            raise EmailInvalido
        object.__setattr__(self, "endereco", normalizado)

    @property
    def nome_de_usuario(self) -> str:
        return self.endereco.split("@", 1)[0]

    def __str__(self) -> str:
        return self.endereco
