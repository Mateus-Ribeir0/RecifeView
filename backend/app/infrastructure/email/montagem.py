import logging

from app.application.portas.contas import EnvioDeEmail
from app.infrastructure.email.caixa_de_saida_local import CaixaDeSaidaLocal
from app.infrastructure.email.envio_por_smtp import EnvioPorSmtp
from app.infrastructure.settings import Configuracao

registro_de_log = logging.getLogger(__name__)


def montar_envio_de_email(configuracao: Configuracao) -> EnvioDeEmail:
    """Sem servidor SMTP configurado, os e-mails ficam em arquivos (o provedor está em aberto)."""
    servidor = configuracao.servidor_smtp
    if servidor is None:
        registro_de_log.info("E-mails na caixa de saída local: %s", configuracao.pasta_dos_emails)
        return CaixaDeSaidaLocal(configuracao.pasta_dos_emails)
    registro_de_log.info("E-mails saem pelo servidor SMTP %s", servidor.endereco)
    return EnvioPorSmtp(servidor)
