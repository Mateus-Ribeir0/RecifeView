from dataclasses import dataclass

from app.application.portas.contribuicoes import ContribuicaoRepository, OcorrenciaDoPainel
from app.application.portas.encaminhamentos import EncaminhamentosDosRelatos
from app.domain.contribuicao.conferencia import chave_da_contribuicao
from app.domain.contribuicao.contribuicao import SITUACAO_NA_BASE
from app.domain.encaminhamento.encaminhamento import Encaminhamento


@dataclass(frozen=True)
class OcorrenciaDoFormulario:
    ocorrencia: OcorrenciaDoPainel
    chave_registro: int | None
    encaminhamento: Encaminhamento | None


@dataclass(frozen=True)
class PaginaDoFormulario:
    itens: list[OcorrenciaDoFormulario]
    total: int


@dataclass(frozen=True)
class ListarOcorrenciasDoFormulario:
    """Só a ocorrência que já entrou na base tem chave: é ela que pode seguir para um órgão."""

    contribuicoes: ContribuicaoRepository
    encaminhamentos: EncaminhamentosDosRelatos

    def executar(self, limite: int, deslocamento: int) -> PaginaDoFormulario:
        pagina = self.contribuicoes.listar_ocorrencias(limite, deslocamento)
        encaminhados = self.encaminhamentos.ultimos_por_relato([item.id for item in pagina.itens])
        itens = [
            OcorrenciaDoFormulario(
                item,
                chave_da_contribuicao(item.id) if item.situacao == SITUACAO_NA_BASE else None,
                encaminhados.get(item.id),
            )
            for item in pagina.itens
        ]
        return PaginaDoFormulario(itens, pagina.total)
