import hashlib
import shutil
from pathlib import Path, PurePath
from uuid import uuid4

from app.application.portas.importacoes import ArquivoRecebido
from app.domain.erros import ArquivoGrandeDemais


class RecebimentoLocal:
    def __init__(self, pasta: Path, nome: str, limite_em_bytes: int) -> None:
        self._pasta = pasta
        self._nome = nome
        self._limite = limite_em_bytes
        self._tamanho = 0
        self._hash = hashlib.sha256()
        self._pasta.mkdir(parents=True, exist_ok=True)
        self._destino = (pasta / "original").open("wb")

    def gravar(self, bloco: bytes) -> None:
        self._tamanho += len(bloco)
        if self._tamanho > self._limite:
            self.abandonar()
            raise ArquivoGrandeDemais
        self._hash.update(bloco)
        self._destino.write(bloco)

    def concluir(self) -> ArquivoRecebido:
        self._destino.close()
        return ArquivoRecebido(self._pasta.name, self._nome, self._tamanho, self._hash.hexdigest())

    def abandonar(self) -> None:
        self._destino.close()
        shutil.rmtree(self._pasta, ignore_errors=True)


class ArmazenamentoLocal:
    """Versão local da camada bruta. S3 ou schema `raw` continua em aberto (ADR 0007)."""

    def __init__(self, pasta: Path, limite_em_bytes: int) -> None:
        self._pasta = pasta
        self._limite = limite_em_bytes

    def iniciar_recebimento(self, nome: str) -> RecebimentoLocal:
        return RecebimentoLocal(self._pasta / uuid4().hex, nome, self._limite)

    def localizar(self, referencia: str) -> Path:
        return self._pasta / PurePath(referencia).name / "original"

    def remover(self, referencia: str) -> None:
        shutil.rmtree(self._pasta / PurePath(referencia).name, ignore_errors=True)
