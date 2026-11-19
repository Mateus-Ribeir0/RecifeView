from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from app.domain.contribuicao.comparacao import (
    DISTINTA,
    ClasseDaComparacao,
    Comparacao,
    Relato,
    comparar_relatos,
)
from app.domain.encaminhamento.encaminhamento import Encaminhamento, OcorrenciaEncaminhavel

DIAS_DA_JANELA_DO_MESMO_PROBLEMA = 30


@dataclass(frozen=True)
class MesmoProblema:
    encaminhamento: Encaminhamento
    comparacao: Comparacao

    @property
    def e_certo(self) -> bool:
        return self.comparacao.classe is ClasseDaComparacao.MESMA


def _relato(ocorrencia: OcorrenciaEncaminhavel) -> Relato | None:
    if ocorrencia.data_abertura is None:
        return None
    return Relato(
        data=ocorrencia.data_abertura,
        bairro=ocorrencia.bairro_oficial,
        categoria=ocorrencia.categoria,
        servico_codigo=ocorrencia.servico_codigo,
        id_local=ocorrencia.id_local,
        numero_informado=ocorrencia.numero_informado,
    )


def comparar_ocorrencias(a: OcorrenciaEncaminhavel, b: OcorrenciaEncaminhavel) -> Comparacao:
    """A regra do pente fino (ADR 0009). O id_local só vale dentro da fonte (docs/dados.md)."""
    if a.chave_registro == b.chave_registro or a.fonte != b.fonte:
        return DISTINTA
    relato_a, relato_b = _relato(a), _relato(b)
    if relato_a is None or relato_b is None:
        return DISTINTA
    return comparar_relatos(relato_a, relato_b)


def encontrar_mesmo_problema(
    ocorrencia: OcorrenciaEncaminhavel, candidatos: Iterable[Encaminhamento]
) -> list[MesmoProblema]:
    parecidos = [
        MesmoProblema(candidato, comparar_ocorrencias(ocorrencia, candidato.ocorrencia))
        for candidato in candidatos
    ]
    encontrados = [item for item in parecidos if item.comparacao.classe is not DISTINTA.classe]
    return sorted(encontrados, key=lambda item: item.comparacao.pontuacao, reverse=True)


def encontrar_mesmo_problema_de_cada(
    encaminhamentos: Sequence[Encaminhamento], candidatos: Sequence[Encaminhamento]
) -> dict[int, list[MesmoProblema]]:
    return {
        encaminhamento.id: encontrar_mesmo_problema(
            encaminhamento.ocorrencia,
            (item for item in candidatos if item.id != encaminhamento.id),
        )
        for encaminhamento in encaminhamentos
    }


def agrupar_mesmo_problema(encaminhamentos: Sequence[Encaminhamento]) -> list[list[Encaminhamento]]:
    """Junta por ligação: se A é o mesmo problema que B e B que C, os três vão para um grupo só."""
    grupo_de: dict[int, int] = {item.id: item.id for item in encaminhamentos}

    def raiz(identificador: int) -> int:
        while grupo_de[identificador] != identificador:
            identificador = grupo_de[identificador]
        return identificador

    for posicao, primeiro in enumerate(encaminhamentos):
        for segundo in encaminhamentos[posicao + 1 :]:
            comparacao = comparar_ocorrencias(primeiro.ocorrencia, segundo.ocorrencia)
            if comparacao.classe is not DISTINTA.classe:
                grupo_de[raiz(segundo.id)] = raiz(primeiro.id)
    grupos: dict[int, list[Encaminhamento]] = {}
    for item in encaminhamentos:
        grupos.setdefault(raiz(item.id), []).append(item)
    return [grupo for grupo in grupos.values() if len(grupo) > 1]
