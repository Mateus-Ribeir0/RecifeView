import smtplib
from email.message import EmailMessage
from typing import Any, ClassVar, Self

import pytest
from pydantic import SecretStr, ValidationError

from app.application.portas.contas import EnvioDeEmailFalhou, MensagemDeEmail
from app.infrastructure.email.caixa_de_saida_local import CaixaDeSaidaLocal
from app.infrastructure.email.envio_por_smtp import EnvioPorSmtp, SegurancaDoSmtp, ServidorSmtp
from app.infrastructure.email.montagem import montar_envio_de_email
from app.infrastructure.settings import Configuracao
from tests.conftest import SEGREDO_DE_TESTE

REMETENTE = "avisos@exemplo.com"
MENSAGEM = MensagemDeEmail("morador@exemplo.com", "Seu código", "Use este código: 123 456")


class ConexaoFalsa:
    abertas: ClassVar[list["ConexaoFalsa"]] = []

    def __init__(self, endereco: str, porta: int, **opcoes: Any) -> None:
        self.endereco, self.porta = endereco, porta
        self.passos: list[str] = []
        self.login_recusado = False
        self.enviados: list[EmailMessage] = []
        ConexaoFalsa.abertas.append(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.passos.append("quit")

    def starttls(self, **_: object) -> None:
        self.passos.append("starttls")

    def login(self, usuario: str, senha: str) -> None:
        if senha == "errada":
            raise smtplib.SMTPAuthenticationError(535, b"recusado")
        self.passos.append(f"login {usuario}")

    def send_message(self, email: EmailMessage) -> None:
        self.enviados.append(email)

    def close(self) -> None:
        self.passos.append("close")


class ConexaoCifradaFalsa(ConexaoFalsa):
    pass


@pytest.fixture(autouse=True)
def smtp_falso(monkeypatch: pytest.MonkeyPatch) -> None:
    ConexaoFalsa.abertas = []
    monkeypatch.setattr(smtplib, "SMTP", ConexaoFalsa)
    monkeypatch.setattr(smtplib, "SMTP_SSL", ConexaoCifradaFalsa)


def servidor(**mudancas: Any) -> ServidorSmtp:
    dados: dict[str, Any] = {
        "endereco": "smtp.exemplo.com",
        "porta": 587,
        "remetente": REMETENTE,
        "usuario": REMETENTE,
        "senha": SecretStr("senha-de-app"),
    }
    return ServidorSmtp(**(dados | mudancas))


def configuracao(**mudancas: Any) -> Configuracao:
    return Configuracao(
        _env_file=None,
        url_do_banco="postgresql+psycopg://teste@localhost/nao-usado",
        segredo_jwt=SecretStr(SEGREDO_DE_TESTE),
        **mudancas,
    )


def test_starttls_autentica_e_envia_em_nome_do_recifeview() -> None:
    EnvioPorSmtp(servidor()).enviar(MENSAGEM)

    conexao = ConexaoFalsa.abertas[0]
    assert conexao.passos == ["starttls", f"login {REMETENTE}", "quit"]
    email = conexao.enviados[0]
    assert email["From"] == f"RecifeView <{REMETENTE}>"
    assert email["To"] == MENSAGEM.para
    assert email["Subject"] == MENSAGEM.assunto
    assert "123 456" in email.get_content()


def test_ssl_cifra_desde_a_conexao() -> None:
    EnvioPorSmtp(servidor(porta=465, seguranca=SegurancaDoSmtp.SSL)).enviar(MENSAGEM)

    conexao = ConexaoFalsa.abertas[0]
    assert isinstance(conexao, ConexaoCifradaFalsa)
    assert "starttls" not in conexao.passos


def test_servidor_sem_usuario_envia_sem_autenticar() -> None:
    EnvioPorSmtp(servidor(usuario=None, senha=None)).enviar(MENSAGEM)

    assert ConexaoFalsa.abertas[0].passos == ["starttls", "quit"]


def test_senha_recusada_vira_falha_de_envio() -> None:
    with pytest.raises(EnvioDeEmailFalhou):
        EnvioPorSmtp(servidor(senha=SecretStr("errada"))).enviar(MENSAGEM)


def test_servidor_fora_do_ar_vira_falha_de_envio(monkeypatch: pytest.MonkeyPatch) -> None:
    def recusar(*_: object, **__: object) -> None:
        raise ConnectionRefusedError

    monkeypatch.setattr(smtplib, "SMTP", recusar)

    with pytest.raises(EnvioDeEmailFalhou):
        EnvioPorSmtp(servidor()).enviar(MENSAGEM)


def test_sem_servidor_smtp_os_emails_ficam_na_caixa_local() -> None:
    assert isinstance(montar_envio_de_email(configuracao()), CaixaDeSaidaLocal)


def test_com_servidor_smtp_os_emails_saem_por_ele() -> None:
    envio = montar_envio_de_email(
        configuracao(smtp_servidor="smtp.exemplo.com", smtp_usuario=REMETENTE)
    )

    assert isinstance(envio, EnvioPorSmtp)


def test_remetente_padrao_e_o_usuario_do_smtp() -> None:
    ajustes = configuracao(smtp_servidor="smtp.exemplo.com", smtp_usuario=REMETENTE)

    assert ajustes.servidor_smtp is not None
    assert ajustes.servidor_smtp.remetente == REMETENTE


def test_variaveis_vazias_desligam_o_smtp() -> None:
    ajustes = configuracao(smtp_servidor="", smtp_usuario="", smtp_senha="")

    assert ajustes.servidor_smtp is None


def test_servidor_sem_remetente_nem_usuario_e_recusado() -> None:
    with pytest.raises(ValidationError):
        configuracao(smtp_servidor="smtp.exemplo.com")
