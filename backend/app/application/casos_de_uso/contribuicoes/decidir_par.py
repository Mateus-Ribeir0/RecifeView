from dataclasses import dataclass
from uuid import UUID

from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.portas.contribuicoes import DecisaoRegistrada
from app.domain.contribuicao.contribuicao import DecisaoDoPar
from app.domain.erros import ParNaoEncontrado


@dataclass(frozen=True)
class DecidirPar:
    servicos: ServicosDeContribuicoes

    def executar(self, par_id: int, decisao: DecisaoDoPar, usuario_id: UUID) -> None:
        registrada = DecisaoRegistrada(decisao, usuario_id, self.servicos.relogio.agora())
        if not self.servicos.contribuicoes.decidir_par(par_id, registrada):
            raise ParNaoEncontrado
