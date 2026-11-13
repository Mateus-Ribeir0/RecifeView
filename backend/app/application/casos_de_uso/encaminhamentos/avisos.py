from dataclasses import dataclass

from app.application.portas.encaminhamentos import DestinatariosDosAvisos, EntregaDeAvisos
from app.domain.encaminhamento.avisos import (
    SITUACOES_QUE_AVISAM_O_CIDADAO,
    aviso_a_gestao,
    aviso_ao_cidadao,
)
from app.domain.encaminhamento.encaminhamento import AutorDoEvento, Encaminhamento


@dataclass(frozen=True)
class AvisosDoCiclo:
    """Cada mudança avisa quem precisa saber. A entrega não interrompe a mudança se falhar."""

    destinatarios: DestinatariosDosAvisos
    entrega: EntregaDeAvisos
    endereco_do_site: str

    def avisar(self, encaminhamento: Encaminhamento, autor: AutorDoEvento) -> None:
        if autor is AutorDoEvento.ORGAO:
            self._avisar_quem_encaminhou(encaminhamento)
        if encaminhamento.situacao in SITUACOES_QUE_AVISAM_O_CIDADAO:
            self._avisar_quem_acompanha(encaminhamento)

    def _avisar_quem_encaminhou(self, encaminhamento: Encaminhamento) -> None:
        email = self.destinatarios.email_de_quem_encaminhou(encaminhamento.id)
        if email:
            self.entrega.entregar(email, aviso_a_gestao(encaminhamento, self.endereco_do_site))

    def _avisar_quem_acompanha(self, encaminhamento: Encaminhamento) -> None:
        aviso = aviso_ao_cidadao(encaminhamento, self.endereco_do_site)
        for email in self.destinatarios.emails_de_quem_acompanha(encaminhamento):
            self.entrega.entregar(email, aviso)
