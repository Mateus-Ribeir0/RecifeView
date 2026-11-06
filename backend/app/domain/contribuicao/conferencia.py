from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.domain.contribuicao.comparacao import (
    ClasseDaComparacao,
    Comparacao,
    Relato,
    comparar_relatos,
)
from app.domain.contribuicao.enderecos import canonizar_logradouro
from app.domain.fontes import Fonte
from app.domain.importacao.chaves import chave_base
from app.domain.importacao.registro import EnderecoDaLinha, RegistroDeDemanda

AMOSTRAS_MOSTRADAS = 20


@dataclass(frozen=True)
class RelatoGuardado:
    contribuicao_id: UUID
    relato: Relato
    rotulo: str


@dataclass(frozen=True)
class Coincidencia:
    contribuicao_id: UUID
    comparacao: Comparacao
    descricao: str
    chave_registro: int | None = None

    @property
    def classe(self) -> ClasseDaComparacao:
        return self.comparacao.classe

    def para_dicionario(self) -> dict[str, Any]:
        return {
            "contribuicao_id": str(self.contribuicao_id),
            "classe": self.classe.value,
            "chave_registro": self.chave_registro,
        }


@dataclass
class ResultadoDaConferencia:
    comparadas: int = 0
    sem_endereco: int = 0
    coincidencias: list[Coincidencia] = field(default_factory=list)

    def da_classe(self, classe: ClasseDaComparacao) -> list[Coincidencia]:
        return [item for item in self.coincidencias if item.classe is classe]

    def resumir(self) -> dict[str, int]:
        return {
            "comparadas": self.comparadas,
            "sem_endereco": self.sem_endereco,
            "certas": len(self.da_classe(ClasseDaComparacao.MESMA)),
            "provaveis": len(self.da_classe(ClasseDaComparacao.PROVAVEL)),
        }


def chave_da_contribuicao(contribuicao_id: UUID) -> int:
    """A mesma chave que a importação gera para a linha do pacote, sem depender de consulta."""
    return chave_base(Fonte.FORMULARIO.value, {"id_registro": str(contribuicao_id)})


def relato_da_linha(registro: RegistroDeDemanda, endereco: EnderecoDaLinha | None) -> Relato | None:
    if registro.data_abertura is None:
        return None
    return Relato(
        data=registro.data_abertura,
        bairro=registro.bairro_oficial,
        categoria=registro.categoria,
        servico_codigo=registro.servico_codigo,
        logradouro=canonizar_logradouro(endereco.logradouro) if endereco else None,
        numero=endereco.numero if endereco else None,
        id_local=registro.id_local,
        numero_informado=bool(registro.numero_informado),
    )


def descrever_coincidencia(rotulo: str, comparacao: Comparacao) -> str:
    return f"{rotulo}: {', '.join(comparacao.motivos).lower()}"


class ConferenciaDoArquivo:
    """Cruza cada linha de um arquivo com os relatos do formulário, sem guardar a linha."""

    def __init__(self, relatos: Iterable[RelatoGuardado]) -> None:
        self._blocos: dict[tuple[str | None, str | None], list[RelatoGuardado]] = defaultdict(list)
        for guardado in relatos:
            self._blocos[(guardado.relato.bairro, guardado.relato.categoria)].append(guardado)
        self._melhores: dict[UUID, Coincidencia] = {}
        self._resultado = ResultadoDaConferencia()

    def conferir(self, registro: RegistroDeDemanda, endereco: EnderecoDaLinha | None) -> None:
        candidatos = self._blocos.get((registro.bairro_oficial, registro.categoria))
        if not candidatos:
            return
        relato = relato_da_linha(registro, endereco)
        if relato is None:
            return
        self._resultado.comparadas += 1
        if endereco is None and registro.id_local is None:
            self._resultado.sem_endereco += 1
            return
        for guardado in candidatos:
            self._guardar_se_for_melhor(guardado, comparar_relatos(guardado.relato, relato))

    def _guardar_se_for_melhor(self, guardado: RelatoGuardado, comparacao: Comparacao) -> None:
        if comparacao.classe is ClasseDaComparacao.DISTINTA:
            return
        atual = self._melhores.get(guardado.contribuicao_id)
        if atual is None or comparacao.pontuacao > atual.comparacao.pontuacao:
            self._melhores[guardado.contribuicao_id] = Coincidencia(
                guardado.contribuicao_id,
                comparacao,
                descrever_coincidencia(guardado.rotulo, comparacao),
            )

    def concluir(self) -> ResultadoDaConferencia:
        self._resultado.coincidencias = list(self._melhores.values())
        return self._resultado
