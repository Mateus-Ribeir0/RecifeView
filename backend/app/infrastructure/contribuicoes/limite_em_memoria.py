import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

from app.application.portas.relogio import Relogio

ENVIOS_POR_JANELA = 12
JANELA_DOS_ENVIOS = timedelta(minutes=10)


class LimiteEmMemoria:
    """Conta os envios recentes por origem, sem gravar nada: a contagem some ao reiniciar."""

    def __init__(self, relogio: Relogio) -> None:
        self._relogio = relogio
        self._envios: dict[str, deque[datetime]] = defaultdict(deque)
        self._trava = threading.Lock()

    def permitir(self, origem: str) -> bool:
        agora = self._relogio.agora()
        with self._trava:
            self._esquecer_antigos(agora)
            envios = self._envios[origem]
            if len(envios) >= ENVIOS_POR_JANELA:
                return False
            envios.append(agora)
            return True

    def _esquecer_antigos(self, agora: datetime) -> None:
        for origem in list(self._envios):
            envios = self._envios[origem]
            while envios and agora - envios[0] > JANELA_DOS_ENVIOS:
                envios.popleft()
            if not envios:
                del self._envios[origem]
