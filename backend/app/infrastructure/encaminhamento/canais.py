import json
import logging
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from pydantic import SecretStr

from app.application.portas.contas import EnvioDeEmail, EnvioDeEmailFalhou, MensagemDeEmail
from app.application.portas.encaminhamentos import EnvioAoOrgaoFalhou
from app.domain.encaminhamento.mensagem import MensagemAoOrgao

SEGUNDOS_DE_ESPERA_DO_WEBHOOK = 15
CABECALHOS_DO_WEBHOOK = {"Content-Type": "application/json; charset=utf-8"}

registro_de_log = logging.getLogger(__name__)


class CaixaDeSaidaDosOrgaos:
    """Grava cada mensagem num arquivo, fora do git, enquanto o órgão não tem canal combinado."""

    def __init__(self, pasta: Path) -> None:
        self._pasta = pasta

    def enviar(self, mensagem: MensagemAoOrgao) -> None:
        self._pasta.mkdir(parents=True, exist_ok=True)
        carimbo = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        arquivo = self._pasta / f"{carimbo}-{mensagem.codigo}-{mensagem.orgao.value}.json"
        conteudo = {"assunto": mensagem.assunto, "corpo": mensagem.corpo, "dados": mensagem.dados}
        arquivo.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
        registro_de_log.info("Encaminhamento gravado na caixa de saída local: %s", arquivo.name)


class EnvioPorEmailAoOrgao:
    def __init__(self, emails: EnvioDeEmail, destino: str) -> None:
        self._emails = emails
        self._destino = destino

    def enviar(self, mensagem: MensagemAoOrgao) -> None:
        email = MensagemDeEmail(self._destino, mensagem.assunto, mensagem.corpo)
        try:
            self._emails.enviar(email)
        except EnvioDeEmailFalhou as erro:
            raise EnvioAoOrgaoFalhou from erro


class EnvioPorWebhook:
    def __init__(self, endereco: str, token: SecretStr | None = None) -> None:
        self._endereco = endereco
        self._token = token

    def enviar(self, mensagem: MensagemAoOrgao) -> None:
        corpo = json.dumps(mensagem.dados, ensure_ascii=False).encode()
        requisicao = urllib.request.Request(  # noqa: S310
            self._endereco, data=corpo, headers=self._cabecalhos(), method="POST"
        )
        try:
            with urllib.request.urlopen(  # noqa: S310
                requisicao, timeout=SEGUNDOS_DE_ESPERA_DO_WEBHOOK
            ):
                return
        except (urllib.error.URLError, TimeoutError, OSError) as erro:
            registro_de_log.error("Webhook do órgão %s falhou", mensagem.orgao.value)
            raise EnvioAoOrgaoFalhou from erro

    def _cabecalhos(self) -> dict[str, str]:
        if self._token is None:
            return CABECALHOS_DO_WEBHOOK
        autorizacao = f"Bearer {self._token.get_secret_value()}"
        return {**CABECALHOS_DO_WEBHOOK, "Authorization": autorizacao}
