from dataclasses import dataclass
from datetime import timedelta

from app.application.portas.contribuicoes import ContribuicaoRepository
from app.application.portas.relogio import Relogio
from app.domain.contribuicao.contribuicao import DIAS_DE_GUARDA_DO_ENDERECO


@dataclass(frozen=True)
class ExpurgarEnderecos:
    """Depois do prazo, só o pseudônimo do endereço continua guardado."""

    contribuicoes: ContribuicaoRepository
    relogio: Relogio

    def executar(self) -> int:
        agora = self.relogio.agora()
        limite = agora - timedelta(days=DIAS_DE_GUARDA_DO_ENDERECO)
        return self.contribuicoes.expurgar_enderecos(limite, agora)
