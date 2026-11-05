from typing import NoReturn

from app.domain.importacao.relatorio import MotivoDeDescarte


class LinhaRecusada(Exception):
    def __init__(self, motivo: MotivoDeDescarte) -> None:
        super().__init__(motivo.value)
        self.motivo = motivo


def recusar(motivo: MotivoDeDescarte) -> NoReturn:
    raise LinhaRecusada(motivo)
