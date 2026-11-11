from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.encaminhamento.orgaos import Orgao, orgao_da_fonte

INDICACOES_MINIMAS_PARA_SUGERIR = 30
PERCENTUAL = 100

# Categorias do 156 que a Câmara não usa como tema caem no tema mais próximo.
TEMA_NA_CAMARA: dict[str, str] = {
    "LUMINARIAS": "ILUMINACAO PUBLICA",
    "POSTE": "ILUMINACAO PUBLICA",
    "ILUMINACAO PROVISORIA": "ILUMINACAO PUBLICA",
    "VAO DE REDE": "ILUMINACAO PUBLICA",
    "COLETA URBANA": "LIMPEZA URBANA",
    "COLETA SELETIVA": "LIMPEZA URBANA",
    "PLANEJAMENTO DE LIMPEZA URBANA": "LIMPEZA URBANA",
    "CALCADAS ARVORES": "ARBORIZACAO",
    "SEMENTEIRA": "ARBORIZACAO",
    "MACRODRENAGEM": "DRENAGEM",
    "TERRAPLENAGEM": "PAVIMENTACAO",
    "ESTUDO ASFALTO": "PAVIMENTACAO",
    "SEMAFOROS": "TRANSITO/SINALIZACAO",
    "REPOSICAO DE PLACAS": "TRANSITO/SINALIZACAO",
    "DENUNCIA VEICULO": "TRANSITO/SINALIZACAO",
}


class MotivoDaSugestao(StrEnum):
    APONTADO_NO_REGISTRO = "apontado_no_registro"
    MAIS_CITADO_NO_TEMA = "mais_citado_no_tema"
    SEM_SUGESTAO = "sem_sugestao"


@dataclass(frozen=True)
class CitacoesDoTema:
    """Quantas indicações da Câmara do tema citam cada órgão, com o nome que a fonte usa."""

    tema: str
    total: int = 0
    por_nome_na_fonte: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ParticipacaoDoOrgao:
    orgao: Orgao
    indicacoes: int
    pct: float


@dataclass(frozen=True)
class SugestaoDeDestino:
    orgao: Orgao | None
    motivo: MotivoDaSugestao
    tema: str | None = None
    indicacoes_do_tema: int = 0
    participacoes: list[ParticipacaoDoOrgao] = field(default_factory=list)


def tema_na_camara(categoria: str | None) -> str | None:
    if not categoria:
        return None
    return TEMA_NA_CAMARA.get(categoria, categoria)


def medir_participacoes(citacoes: CitacoesDoTema) -> list[ParticipacaoDoOrgao]:
    """O percentual é sobre todas as indicações do tema, inclusive as que não citam órgão."""
    if citacoes.total == 0:
        return []
    contagem: Counter[Orgao] = Counter()
    for nome, indicacoes in citacoes.por_nome_na_fonte.items():
        orgao = orgao_da_fonte(nome)
        if orgao is not None:
            contagem[orgao] += indicacoes
    return [
        ParticipacaoDoOrgao(orgao, indicacoes, indicacoes / citacoes.total * PERCENTUAL)
        for orgao, indicacoes in contagem.most_common()
    ]


def sugerir_destino(
    orgao_na_fonte: str | None, citacoes: CitacoesDoTema | None
) -> SugestaoDeDestino:
    participacoes = medir_participacoes(citacoes) if citacoes else []
    tema = citacoes.tema if citacoes else None
    total = citacoes.total if citacoes else 0
    apontado = orgao_da_fonte(orgao_na_fonte)
    if apontado is not None:
        return SugestaoDeDestino(
            apontado, MotivoDaSugestao.APONTADO_NO_REGISTRO, tema, total, participacoes
        )
    if participacoes and total >= INDICACOES_MINIMAS_PARA_SUGERIR:
        mais_citado = participacoes[0].orgao
        return SugestaoDeDestino(
            mais_citado, MotivoDaSugestao.MAIS_CITADO_NO_TEMA, tema, total, participacoes
        )
    return SugestaoDeDestino(None, MotivoDaSugestao.SEM_SUGESTAO, tema, total, participacoes)
