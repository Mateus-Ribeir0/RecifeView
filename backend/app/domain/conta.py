import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self
from uuid import UUID

from app.domain.erros import CadastroInvalido

DIGITOS_DO_CODIGO = 6
VALIDADE_DO_CODIGO = timedelta(minutes=15)
TENTATIVAS_POR_CODIGO = 5
INTERVALO_ENTRE_CODIGOS = timedelta(seconds=60)

TAMANHO_MINIMO_DO_NOME = 2
TAMANHO_MAXIMO_DO_NOME = 80
NOME_PERMITIDO = re.compile(r"^[^\W\d_]+(?:[ '-][^\W\d_]+)*$")
ESPACOS = re.compile(r"\s+")


class FinalidadeDoCodigo(StrEnum):
    REDEFINIR_SENHA = "REDEFINIR_SENHA"


def normalizar_nome(nome: str) -> str:
    """Só letras, espaço, hífen e apóstrofo: o nome aparece na tela e não pode virar recado."""
    limpo = ESPACOS.sub(" ", nome).strip()
    if not TAMANHO_MINIMO_DO_NOME <= len(limpo) <= TAMANHO_MAXIMO_DO_NOME:
        raise CadastroInvalido("nome", "Informe um nome com 2 a 80 caracteres.")
    if not NOME_PERMITIDO.match(limpo):
        raise CadastroInvalido("nome", "Use só letras, espaço, hífen ou apóstrofo no nome.")
    return limpo


def gerar_codigo() -> str:
    return str(secrets.randbelow(10**DIGITOS_DO_CODIGO)).zfill(DIGITOS_DO_CODIGO)


def calcular_hash_do_codigo(codigo_id: UUID, codigo: str) -> str:
    return hashlib.sha256(f"{codigo_id}:{codigo}".encode()).hexdigest()


@dataclass(frozen=True)
class CodigoDeConta:
    id: UUID
    usuario_id: UUID
    finalidade: FinalidadeDoCodigo
    hash_do_codigo: str
    criado_em: datetime
    expira_em: datetime
    tentativas: int = 0
    usado_em: datetime | None = None

    def pode_ser_usado(self, agora: datetime) -> bool:
        return (
            self.usado_em is None
            and agora < self.expira_em
            and self.tentativas < TENTATIVAS_POR_CODIGO
        )

    def confere(self, digitado: str) -> bool:
        esperado = calcular_hash_do_codigo(self.id, digitado.strip())
        return hmac.compare_digest(esperado, self.hash_do_codigo)

    def foi_emitido_ha_pouco(self, agora: datetime) -> bool:
        return agora - self.criado_em < INTERVALO_ENTRE_CODIGOS

    def com_tentativa(self) -> Self:
        return replace(self, tentativas=self.tentativas + 1)

    def usado(self, agora: datetime) -> Self:
        return replace(self, usado_em=agora)
