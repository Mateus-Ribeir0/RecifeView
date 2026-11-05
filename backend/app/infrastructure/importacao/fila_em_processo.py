import logging
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

registro_de_log = logging.getLogger(__name__)


def _registrar_falha(tarefa: Future[None]) -> None:
    erro = tarefa.exception()
    if erro is not None:
        registro_de_log.error("Falha numa tarefa de importação", exc_info=erro)


class FilaEmProcesso:
    """Uma tarefa por vez, dentro da API. A versão com worker separado depende da ADR 0007."""

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="importacao")

    def enfileirar(self, tarefa: Callable[[], None]) -> None:
        self._executor.submit(tarefa).add_done_callback(_registrar_falha)
