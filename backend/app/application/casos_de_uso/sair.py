from dataclasses import dataclass

from app.application.portas.acessos import RegistroDeAcessos
from app.application.portas.relogio import Relogio
from app.application.sessoes import GestaoDeSessoes
from app.domain.acesso import EventoDeAcesso, TipoDeEventoDeAcesso
from app.domain.erros import SessaoInvalida


@dataclass(frozen=True)
class Sair:
    sessoes: GestaoDeSessoes
    acessos: RegistroDeAcessos
    relogio: Relogio

    def executar(self, token_de_sessao: str | None) -> None:
        try:
            sessao = self.sessoes.buscar_ativa(token_de_sessao)
        except SessaoInvalida:
            return
        self.sessoes.encerrar(sessao)
        evento = EventoDeAcesso(TipoDeEventoDeAcesso.SAIDA, self.relogio.agora(), sessao.usuario_id)
        self.acessos.registrar(evento)
