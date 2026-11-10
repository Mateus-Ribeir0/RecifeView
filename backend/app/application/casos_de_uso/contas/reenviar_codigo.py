from dataclasses import dataclass

from app.application.casos_de_uso.contas.codigos import CodigosDeConta
from app.application.casos_de_uso.contas.confirmar_email import buscar_por_texto_de_email
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.domain.conta import FinalidadeDoCodigo


@dataclass(frozen=True)
class ReenviarCodigoDeConfirmacao:
    servicos: ServicosDeConta

    def executar(self, email: str) -> None:
        usuario = buscar_por_texto_de_email(self.servicos, email)
        if usuario is not None and usuario.precisa_confirmar_email:
            CodigosDeConta(self.servicos).emitir(usuario, FinalidadeDoCodigo.CONFIRMAR_EMAIL)
