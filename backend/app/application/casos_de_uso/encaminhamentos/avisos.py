from collections.abc import Iterable
from dataclasses import dataclass

from app.application.portas.encaminhamentos import (
    Destinatario,
    DestinatariosDosAvisos,
    EntregaDeAvisos,
)
from app.application.portas.notificacoes import NotificacaoRepository
from app.domain.encaminhamento.avisos import (
    SITUACOES_QUE_AVISAM_O_CIDADAO,
    Aviso,
    aviso_a_gestao,
    aviso_ao_cidadao,
    aviso_de_nova_ocorrencia,
    aviso_de_prazo_vencido,
)
from app.domain.encaminhamento.encaminhamento import (
    AutorDoEvento,
    Encaminhamento,
    SituacaoDoEncaminhamento,
)
from app.domain.notificacao import NovaNotificacao


@dataclass(frozen=True)
class AvisosDoCiclo:
    """Cada mudança avisa quem precisa saber: no sino sempre, por e-mail se a pessoa quiser.

    A entrega do e-mail não interrompe a mudança se falhar.
    """

    destinatarios: DestinatariosDosAvisos
    entrega: EntregaDeAvisos
    notificacoes: NotificacaoRepository
    endereco_do_site: str

    def avisar(self, encaminhamento: Encaminhamento, autor: AutorDoEvento) -> None:
        if autor is AutorDoEvento.ORGAO:
            self._avisar_quem_encaminhou(encaminhamento)
        if encaminhamento.situacao in SITUACOES_QUE_AVISAM_O_CIDADAO:
            aviso = aviso_ao_cidadao(encaminhamento, self.endereco_do_site)
            self._entregar(self.destinatarios.cidadaos_que_acompanham(encaminhamento), aviso)
        if encaminhamento.situacao is SituacaoDoEncaminhamento.ENVIADO:
            aviso = aviso_de_nova_ocorrencia(encaminhamento, self.endereco_do_site)
            self._entregar(self.destinatarios.pessoas_do_orgao(encaminhamento.orgao), aviso)

    def avisar_prazo_vencido(self, encaminhamento: Encaminhamento) -> None:
        aviso = aviso_de_prazo_vencido(encaminhamento, self.endereco_do_site)
        self._entregar(self.destinatarios.pessoas_do_orgao(encaminhamento.orgao), aviso)

    def _avisar_quem_encaminhou(self, encaminhamento: Encaminhamento) -> None:
        destinatario = self.destinatarios.gestor_que_encaminhou(encaminhamento.id)
        if destinatario:
            self._entregar([destinatario], aviso_a_gestao(encaminhamento, self.endereco_do_site))

    def _entregar(self, destinatarios: Iterable[Destinatario], aviso: Aviso) -> None:
        for destinatario in destinatarios:
            self.notificacoes.criar(
                NovaNotificacao(destinatario.usuario_id, aviso.assunto, aviso.resumo, aviso.caminho)
            )
            if destinatario.recebe_email:
                self.entrega.entregar(destinatario.email, aviso)
