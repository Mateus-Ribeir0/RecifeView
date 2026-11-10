from dataclasses import dataclass
from datetime import date, timedelta
from uuid import UUID

from app.application.portas.contribuicoes import (
    ContribuicaoRepository,
    FiltroDaCidade,
    OcorrenciaDaCidade,
)
from app.application.portas.relogio import Relogio
from app.domain.cidade import (
    DIAS_DA_VISAO_DO_CIDADAO,
    SituacaoPublica,
    faixa_de_numeracao,
    situacao_publica,
)
from app.domain.contribuicao.catalogo import SERVICOS_POR_CODIGO, TEMAS_DO_FORMULARIO

TEMA_POR_SERVICO = {
    servico.codigo: tema for tema in TEMAS_DO_FORMULARIO for servico in tema.servicos
}


@dataclass(frozen=True)
class OcorrenciaPublica:
    """O que o cidadão vê de um relato: nunca o número exato nem o texto escrito."""

    id: UUID
    data_relato: date
    servico: str
    tema: str
    bairro_oficial: str
    bairro: str
    rpa: str
    via: str | None
    faixa_de_numeracao: str | None
    relatos: int
    sem_retorno: int
    situacao: SituacaoPublica


def _categorias_do_tema(tema: str | None) -> tuple[str, ...]:
    escolhido = next((item for item in TEMAS_DO_FORMULARIO if item.chave == tema), None)
    if escolhido is None:
        return ()
    return tuple(sorted({servico.categoria for servico in escolhido.servicos}))


def _publicar(linha: OcorrenciaDaCidade) -> OcorrenciaPublica:
    servico = SERVICOS_POR_CODIGO.get(linha.servico_codigo)
    tema = TEMA_POR_SERVICO.get(linha.servico_codigo)
    return OcorrenciaPublica(
        id=linha.id,
        data_relato=linha.data_relato,
        servico=servico.rotulo if servico else linha.servico,
        tema=tema.rotulo if tema else "Outros",
        bairro_oficial=linha.bairro_oficial,
        bairro=linha.bairro,
        rpa=linha.rpa,
        via=linha.via_reconhecida,
        faixa_de_numeracao=faixa_de_numeracao(linha.numero) if linha.via_reconhecida else None,
        relatos=linha.relatos,
        sem_retorno=linha.sem_retorno,
        situacao=situacao_publica(linha.situacao, linha.tem_dupla_aberta),
    )


@dataclass(frozen=True)
class ListarOcorrenciasDaCidade:
    contribuicoes: ContribuicaoRepository
    relogio: Relogio

    def executar(self, bairro: str | None, tema: str | None) -> list[OcorrenciaPublica]:
        desde = self.relogio.agora().date() - timedelta(days=DIAS_DA_VISAO_DO_CIDADAO)
        filtro = FiltroDaCidade(desde, bairro or None, _categorias_do_tema(tema))
        return [_publicar(linha) for linha in self.contribuicoes.ocorrencias_da_cidade(filtro)]
