from dataclasses import dataclass

from app.application.casos_de_uso.encaminhamentos.servicos import (
    ServicosDeEncaminhamento,
    gerar_token_de_retorno,
)
from app.application.portas.encaminhamentos import EnvioAoOrgaoFalhou
from app.domain.encaminhamento.encaminhamento import Encaminhamento
from app.domain.encaminhamento.mensagem import montar_lembrete


@dataclass(frozen=True)
class ResultadoDosLembretes:
    enviados: int = 0
    falhas: int = 0


@dataclass(frozen=True)
class LembrarOrgaos:
    """Para o agendador: um lembrete por encaminhamento cujo prazo venceu sem resposta final."""

    servicos: ServicosDeEncaminhamento

    def executar(self) -> ResultadoDosLembretes:
        hoje = self.servicos.relogio.agora().date()
        vencidos = self.servicos.encaminhamentos.vencidos_sem_lembrete(hoje)
        enviados = sum(1 for item in vencidos if self._lembrar(item))
        return ResultadoDosLembretes(enviados, len(vencidos) - enviados)

    def _lembrar(self, encaminhamento: Encaminhamento) -> bool:
        agora = self.servicos.relogio.agora()
        token = gerar_token_de_retorno(agora)
        link = self.servicos.link_de_retorno(token)
        lembrete = montar_lembrete(encaminhamento, link, token.guardado.expira_em.date())
        try:
            self.servicos.despacho.enviar(lembrete)
        except EnvioAoOrgaoFalhou:
            return False
        self.servicos.encaminhamentos.registrar_lembrete(encaminhamento.id, token.guardado, agora)
        return True
