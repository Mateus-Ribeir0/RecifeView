import logging

from app.application.portas.contas import EnvioDeEmail, EnvioDeEmailFalhou, MensagemDeEmail
from app.domain.encaminhamento.avisos import Aviso

registro_de_log = logging.getLogger(__name__)


class AvisosPorEmail:
    """O aviso não pode desfazer a resposta do órgão: a falha fica no log, sem o endereço."""

    def __init__(self, emails: EnvioDeEmail) -> None:
        self._emails = emails

    def entregar(self, para: str, aviso: Aviso) -> None:
        try:
            self._emails.enviar(MensagemDeEmail(para, aviso.assunto, aviso.corpo))
        except EnvioDeEmailFalhou:
            registro_de_log.warning("Aviso não entregue: %s", aviso.assunto)
