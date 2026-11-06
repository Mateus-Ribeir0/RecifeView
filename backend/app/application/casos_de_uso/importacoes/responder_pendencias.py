from dataclasses import dataclass, field, replace

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.casos_de_uso.importacoes.validar_importacao import ValidarImportacao
from app.domain.importacao.datas import FormatoDeData
from app.domain.importacao.decisoes import (
    Decisoes,
    PoliticaDeDatasInvalidas,
    PoliticaDeDuplicados,
    PoliticaDeRepetidos,
    PoliticaEntreCanais,
)
from app.domain.importacao.importacao import Importacao, StatusDaImportacao


@dataclass(frozen=True)
class RespostasDePendencias:
    formato_de_data: FormatoDeData | None = None
    substituicoes: dict[str, dict[str, str]] = field(default_factory=dict)
    padrao_para_valores: dict[str, str] = field(default_factory=dict)
    datas_invalidas: PoliticaDeDatasInvalidas | None = None
    repetidos_na_base: PoliticaDeRepetidos | None = None
    repetidos_no_arquivo: PoliticaDeDuplicados | None = None
    coincidencias_certas: PoliticaEntreCanais | None = None
    coincidencias_provaveis: PoliticaEntreCanais | None = None


def _combinar(decisoes: Decisoes, respostas: RespostasDePendencias) -> Decisoes:
    substituicoes = {campo: dict(valores) for campo, valores in decisoes.substituicoes.items()}
    for campo, valores in respostas.substituicoes.items():
        substituicoes.setdefault(campo, {}).update(valores)
    return replace(
        decisoes,
        formato_de_data=respostas.formato_de_data or decisoes.formato_de_data,
        substituicoes=substituicoes,
        padrao_para_valores={**decisoes.padrao_para_valores, **respostas.padrao_para_valores},
        datas_invalidas=respostas.datas_invalidas or decisoes.datas_invalidas,
        repetidos_na_base=respostas.repetidos_na_base or decisoes.repetidos_na_base,
        repetidos_no_arquivo=respostas.repetidos_no_arquivo or decisoes.repetidos_no_arquivo,
        coincidencias_certas=respostas.coincidencias_certas or decisoes.coincidencias_certas,
        coincidencias_provaveis=(
            respostas.coincidencias_provaveis or decisoes.coincidencias_provaveis
        ),
    )


@dataclass(frozen=True)
class ResponderPendencias:
    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int, respostas: RespostasDePendencias) -> Importacao:
        importacao = self.servicos.obter(importacao_id)
        importacao.exigir_edicao_aberta()
        atualizada = replace(
            importacao,
            status=StatusDaImportacao.VALIDANDO,
            progresso=0,
            decisoes=_combinar(importacao.decisoes, respostas),
        )
        self.servicos.importacoes.salvar(atualizada)
        validar = ValidarImportacao(self.servicos)
        self.servicos.fila.enfileirar(lambda: validar.executar(importacao_id))
        return atualizada
