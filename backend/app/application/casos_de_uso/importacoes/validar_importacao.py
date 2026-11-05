from collections.abc import Iterator
from dataclasses import asdict, dataclass, replace
from itertools import islice
from typing import Any

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import ComparacaoComABase, TabelaDoArquivo
from app.domain.erros import ArquivoIlegivel
from app.domain.importacao.campos import CAMPOS_DE_DATA, CAMPOS_VERIFICADOS_NO_VOCABULARIO
from app.domain.importacao.datas import formato_de_data_ambiguo, usa_barra_com_ano_no_fim
from app.domain.importacao.decisoes import Decisoes
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.normalizador import NormalizadorDeLinhas, Referencias
from app.domain.importacao.pendencias import (
    Pendencia,
    TipoDePendencia,
    montar_pendencia_de_valores,
    valores_ainda_sem_resposta,
)
from app.domain.importacao.relatorio import RelatorioDeLinhas

LINHAS_PARA_PROVAR_A_DATA = 20_000
LINHAS_DA_PREVIA = 8
TAMANHO_MAXIMO_NA_PREVIA = 60
INTERVALO_DE_PROGRESSO = 5_000
CAMPOS_DA_PREVIA = (
    "fonte",
    "ano",
    "data_abertura",
    "data_ult_movimento",
    "dias_ate_movimento",
    "categoria",
    "servico",
    "orgao",
    "bairro_oficial",
    "rpa",
    "situacao",
)


def _colunas_de_data(tabela: TabelaDoArquivo, decisoes: Decisoes) -> list[int]:
    return [
        indice
        for indice, coluna in enumerate(tabela.colunas)
        if decisoes.mapeamento.get(coluna) in CAMPOS_DE_DATA
    ]


def _valores_de_data(tabela: TabelaDoArquivo, decisoes: Decisoes) -> list[str]:
    indices = _colunas_de_data(tabela, decisoes)
    amostra = islice(tabela.linhas(), LINHAS_PARA_PROVAR_A_DATA)
    return [linha[i] for linha in amostra for i in indices if i < len(linha) and linha[i]]


def _decidir_formato_de_data(tabela: TabelaDoArquivo, decisoes: Decisoes) -> Decisoes:
    if decisoes.formato_de_data is not None:
        return decisoes
    valores = _valores_de_data(tabela, decisoes)
    provado = formato_de_data_ambiguo(valores)
    return replace(decisoes, formato_de_data=provado) if provado else decisoes


def _pendencias_de_valores(
    relatorio: RelatorioDeLinhas, decisoes: Decisoes, referencias: Referencias
) -> list[Pendencia]:
    itens = []
    bairros = valores_ainda_sem_resposta("bairro", relatorio.bairros_desconhecidos, decisoes)
    if bairros:
        itens.append(
            montar_pendencia_de_valores(
                TipoDePendencia.BAIRRO_DESCONHECIDO, "bairro", bairros, list(referencias.bairros)
            )
        )
    for campo in CAMPOS_VERIFICADOS_NO_VOCABULARIO:
        novos = relatorio.valores_novos.get(campo)
        if not novos:
            continue
        restantes = valores_ainda_sem_resposta(campo, novos, decisoes)
        if restantes:
            conhecidos = sorted(
                {
                    valor
                    for (fonte, nome), valores in referencias.vocabularios.items()
                    if nome == campo and fonte in relatorio.fontes
                    for valor in valores
                }
            )
            itens.append(
                montar_pendencia_de_valores(
                    TipoDePendencia.VALOR_NOVO, campo, restantes, conhecidos
                )
            )
    return itens


def _pendencias_de_datas(
    relatorio: RelatorioDeLinhas, decisoes: Decisoes, tabela: TabelaDoArquivo
) -> list[Pendencia]:
    itens = []
    if decisoes.formato_de_data is None and usa_barra_com_ano_no_fim(
        _valores_de_data(tabela, decisoes)
    ):
        itens.append(Pendencia(TipoDePendencia.FORMATO_DE_DATA))
    invalidas = {
        campo: n for campo, n in relatorio.datas_invalidas.items() if campo != "data_abertura"
    }
    if invalidas and decisoes.datas_invalidas is None:
        itens.append(
            Pendencia(
                TipoDePendencia.DATAS_INVALIDAS,
                quantidade=sum(invalidas.values()),
                detalhes=invalidas,
            )
        )
    return itens


def _pendencias_de_repetidos(
    relatorio: RelatorioDeLinhas, decisoes: Decisoes, comparacao: ComparacaoComABase
) -> list[Pendencia]:
    itens = []
    if comparacao.alteradas and decisoes.repetidos_na_base is None:
        itens.append(
            Pendencia(
                TipoDePendencia.REPETIDOS_NA_BASE,
                quantidade=comparacao.alteradas,
                detalhes={"iguais": comparacao.iguais, "alteradas": comparacao.alteradas},
            )
        )
    if relatorio.repetidas_no_arquivo and decisoes.repetidos_no_arquivo is None:
        itens.append(
            Pendencia(
                TipoDePendencia.REPETIDOS_NO_ARQUIVO, quantidade=relatorio.repetidas_no_arquivo
            )
        )
    return itens


def resumir_relatorio(relatorio: RelatorioDeLinhas) -> dict[str, Any]:
    return {
        "lidas": relatorio.lidas,
        "aceitas": relatorio.aceitas,
        "descartes": {motivo.value: n for motivo, n in relatorio.descartes.items()},
        "correcoes": {correcao.value: n for correcao, n in relatorio.correcoes.items()},
        "repetidas_no_arquivo": relatorio.repetidas_no_arquivo,
        "sem_id_local": relatorio.sem_id_local,
        "periodo_inicio": _data_iso(relatorio.primeira_data),
        "periodo_fim": _data_iso(relatorio.ultima_data),
        "fontes": dict(relatorio.fontes),
    }


def _data_iso(data: Any) -> str | None:
    return data.isoformat() if data is not None else None


def _texto_da_previa(valor: object) -> str:
    return "" if valor is None else str(valor)[:TAMANHO_MAXIMO_NA_PREVIA]


def montar_previa(
    tabela: TabelaDoArquivo, normalizador: NormalizadorDeLinhas, colunas_visiveis: list[str]
) -> list[dict[str, dict[str, str]]]:
    indices = [tabela.colunas.index(coluna) for coluna in colunas_visiveis]
    previa = []
    for linha in islice(tabela.linhas(), LINHAS_DA_PREVIA):
        registro = normalizador.normalizar(linha)
        if registro is None:
            continue
        depois = registro._asdict()
        previa.append(
            {
                "antes": {
                    tabela.colunas[i]: _texto_da_previa(linha[i]) for i in indices if i < len(linha)
                },
                "depois": {campo: _texto_da_previa(depois[campo]) for campo in CAMPOS_DA_PREVIA},
            }
        )
    return previa


def colunas_visiveis_na_previa(importacao: Importacao) -> list[str]:
    colunas: list[dict[str, Any]] = importacao.estrutura.get("colunas", [])
    mapeadas = importacao.decisoes.mapeamento
    return [c["nome"] for c in colunas if not c["bloqueada"] and mapeadas.get(c["nome"])]


@dataclass(frozen=True)
class ValidarImportacao:
    """Percorre o arquivo com as decisões atuais e aponta o que ainda precisa de resposta."""

    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int) -> None:
        importacao = self.servicos.obter(importacao_id)
        try:
            self._validar(importacao)
        except ArquivoIlegivel:
            mensagem = "Não foi possível ler o arquivo até o fim. Confira o formato."
            self.servicos.importacoes.salvar(
                replace(importacao, status=StatusDaImportacao.FALHOU, mensagem_de_erro=mensagem)
            )

    def _validar(self, importacao: Importacao) -> None:
        tabela = self.servicos.abrir_tabela(importacao)
        decisoes = _decidir_formato_de_data(tabela, importacao.decisoes)
        importacao = replace(importacao, decisoes=decisoes)
        normalizador = self.servicos.preparar_normalizador(importacao, tabela)
        comparacao = self.servicos.carregador.comparar_com_a_base(
            self._assinaturas(tabela, normalizador)
        )
        referencias = self.servicos.referencias.carregar()
        relatorio = normalizador.relatorio
        itens = [
            *_pendencias_de_datas(relatorio, decisoes, tabela),
            *_pendencias_de_valores(relatorio, decisoes, referencias),
            *_pendencias_de_repetidos(relatorio, decisoes, comparacao),
        ]
        previa = montar_previa(
            tabela,
            self.servicos.criar_normalizador_da_previa(importacao, tabela),
            colunas_visiveis_na_previa(importacao),
        )
        self._concluir(importacao, itens, previa, (relatorio, comparacao))

    def _assinaturas(
        self, tabela: TabelaDoArquivo, normalizador: NormalizadorDeLinhas
    ) -> Iterator[tuple[int, int]]:
        for linha in tabela.linhas():
            registro = normalizador.normalizar(linha)
            if registro is not None:
                yield registro.chave_registro, registro.assinatura

    def _concluir(
        self,
        importacao: Importacao,
        itens: list[Pendencia],
        previa: list[dict[str, dict[str, str]]],
        contagens: tuple[RelatorioDeLinhas, ComparacaoComABase],
    ) -> None:
        relatorio, comparacao = contagens
        resumo = resumir_relatorio(relatorio)
        novas = relatorio.aceitas - comparacao.iguais - comparacao.alteradas
        resumo.update(novas=novas, iguais=comparacao.iguais, alteradas=comparacao.alteradas)
        status = StatusDaImportacao.AGUARDANDO_DECISOES if itens else StatusDaImportacao.PRONTA
        self.servicos.importacoes.salvar(
            replace(
                importacao,
                status=status,
                progresso=0,
                pendencias={
                    "itens": [asdict(item) for item in itens],
                    "resumo": resumo,
                    "previa": previa,
                },
            )
        )
