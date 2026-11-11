import logging
from dataclasses import dataclass
from typing import Protocol

from app.application.portas.contas import EnvioDeEmail
from app.domain.encaminhamento.encaminhamento import CanalDeEnvio
from app.domain.encaminhamento.mensagem import MensagemAoOrgao
from app.domain.encaminhamento.orgaos import Orgao
from app.infrastructure.encaminhamento.canais import (
    CaixaDeSaidaDosOrgaos,
    EnvioPorEmailAoOrgao,
    EnvioPorWebhook,
)
from app.infrastructure.settings import CanalConfigurado, Configuracao

registro_de_log = logging.getLogger(__name__)


class CanalDoOrgao(Protocol):
    def enviar(self, mensagem: MensagemAoOrgao) -> None: ...


@dataclass(frozen=True)
class CanalEscolhido:
    tipo: CanalDeEnvio
    envio: CanalDoOrgao


class DespachoConfigurado:
    """Órgão sem canal configurado recebe pela caixa de saída local."""

    def __init__(self, canais: dict[Orgao, CanalEscolhido], caixa_local: CanalDoOrgao) -> None:
        self._canais = canais
        self._padrao = CanalEscolhido(CanalDeEnvio.LOCAL, caixa_local)

    def canal_de(self, orgao: Orgao) -> CanalDeEnvio:
        return self._canais.get(orgao, self._padrao).tipo

    def enviar(self, mensagem: MensagemAoOrgao) -> None:
        self._canais.get(mensagem.orgao, self._padrao).envio.enviar(mensagem)


def _montar_canal(
    configurado: CanalConfigurado, emails: EnvioDeEmail, caixa_local: CaixaDeSaidaDosOrgaos
) -> CanalEscolhido:
    if configurado.canal is CanalDeEnvio.EMAIL:
        return CanalEscolhido(configurado.canal, EnvioPorEmailAoOrgao(emails, configurado.destino))
    if configurado.canal is CanalDeEnvio.WEBHOOK:
        envio = EnvioPorWebhook(configurado.destino, configurado.token)
        return CanalEscolhido(configurado.canal, envio)
    return CanalEscolhido(CanalDeEnvio.LOCAL, caixa_local)


def montar_despacho(configuracao: Configuracao, emails: EnvioDeEmail) -> DespachoConfigurado:
    caixa_local = CaixaDeSaidaDosOrgaos(configuracao.pasta_dos_encaminhamentos)
    canais = {
        orgao: _montar_canal(configurado, emails, caixa_local)
        for orgao, configurado in configuracao.canais_dos_orgaos.items()
    }
    configurados = ", ".join(
        f"{orgao.value}: {canal.tipo.value}" for orgao, canal in canais.items()
    )
    registro_de_log.info("Canais dos órgãos: %s", configurados or "todos na caixa de saída local")
    return DespachoConfigurado(canais, caixa_local)
