import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.application.portas.contas import MensagemDeEmail

registro_de_log = logging.getLogger(__name__)


class CaixaDeSaidaLocal:
    """Grava cada e-mail num arquivo, fora do git. O provedor de envio real está em aberto."""

    def __init__(self, pasta: Path) -> None:
        self._pasta = pasta

    def enviar(self, mensagem: MensagemDeEmail) -> None:
        self._pasta.mkdir(parents=True, exist_ok=True)
        carimbo = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        arquivo = self._pasta / f"{carimbo}-{uuid4().hex[:8]}.txt"
        conteudo = f"Para: {mensagem.para}\nAssunto: {mensagem.assunto}\n\n{mensagem.corpo}\n"
        arquivo.write_text(conteudo, encoding="utf-8")
        registro_de_log.info("E-mail gravado na caixa de saída local: %s", arquivo.name)
