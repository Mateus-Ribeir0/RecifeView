import logging
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from enum import StrEnum

from pydantic import SecretStr

from app.application.portas.contas import EnvioDeEmailFalhou, MensagemDeEmail

NOME_DO_REMETENTE = "RecifeView"
SEGUNDOS_DE_ESPERA_DO_SERVIDOR = 15

registro_de_log = logging.getLogger(__name__)


class SegurancaDoSmtp(StrEnum):
    STARTTLS = "starttls"
    SSL = "ssl"


@dataclass(frozen=True)
class ServidorSmtp:
    endereco: str
    porta: int
    remetente: str
    seguranca: SegurancaDoSmtp = SegurancaDoSmtp.STARTTLS
    usuario: str | None = None
    senha: SecretStr | None = None


class EnvioPorSmtp:
    def __init__(self, servidor: ServidorSmtp) -> None:
        self._servidor = servidor

    def enviar(self, mensagem: MensagemDeEmail) -> None:
        try:
            with self._conectar() as conexao:
                self._autenticar(conexao)
                conexao.send_message(self._montar(mensagem))
        except smtplib.SMTPAuthenticationError as erro:
            registro_de_log.error("O servidor SMTP recusou o usuário e a senha configurados")
            raise EnvioDeEmailFalhou from erro
        except (smtplib.SMTPException, OSError) as erro:
            registro_de_log.error("Envio por SMTP falhou: %s", type(erro).__name__)
            raise EnvioDeEmailFalhou from erro

    def _conectar(self) -> smtplib.SMTP:
        servidor = self._servidor
        contexto = ssl.create_default_context()
        if servidor.seguranca is SegurancaDoSmtp.SSL:
            return smtplib.SMTP_SSL(
                servidor.endereco,
                servidor.porta,
                timeout=SEGUNDOS_DE_ESPERA_DO_SERVIDOR,
                context=contexto,
            )
        conexao = smtplib.SMTP(
            servidor.endereco, servidor.porta, timeout=SEGUNDOS_DE_ESPERA_DO_SERVIDOR
        )
        try:
            conexao.starttls(context=contexto)
        except (smtplib.SMTPException, OSError):
            conexao.close()
            raise
        return conexao

    def _autenticar(self, conexao: smtplib.SMTP) -> None:
        usuario, senha = self._servidor.usuario, self._servidor.senha
        if usuario and senha:
            conexao.login(usuario, senha.get_secret_value())

    def _montar(self, mensagem: MensagemDeEmail) -> EmailMessage:
        remetente = self._servidor.remetente
        email = EmailMessage()
        email["From"] = formataddr((NOME_DO_REMETENTE, remetente))
        email["To"] = mensagem.para
        email["Subject"] = mensagem.assunto
        email["Date"] = formatdate(localtime=True)
        email["Message-ID"] = make_msgid(domain=remetente.rpartition("@")[2] or None)
        email.set_content(mensagem.corpo)
        return email
