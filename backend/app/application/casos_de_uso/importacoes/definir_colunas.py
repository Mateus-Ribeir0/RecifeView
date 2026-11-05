from dataclasses import dataclass, replace
from datetime import date

from app.application.casos_de_uso.importacoes.analisar_arquivo import colunas_com_uso_fixo
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.casos_de_uso.importacoes.validar_importacao import ValidarImportacao
from app.domain.erros import DecisaoInvalida
from app.domain.fontes import Fonte
from app.domain.importacao.campos import CAMPOS_OBRIGATORIOS, CAMPOS_POR_NOME
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.layouts import LAYOUTS_POR_CODIGO, CodigoDoLayout


@dataclass(frozen=True)
class EscolhaDeColunas:
    fonte: Fonte | None
    data_do_retrato: date
    mapeamento: dict[str, str | None]
    valores_fixos: dict[str, str]


def _exigir_campos_conhecidos(importacao: Importacao, campos: list[str]) -> None:
    layout = LAYOUTS_POR_CODIGO[CodigoDoLayout(importacao.layout or CodigoDoLayout.MANUAL)]
    usos_internos = set(layout.colunas.values())
    desconhecidos = [
        campo for campo in campos if campo not in CAMPOS_POR_NOME and campo not in usos_internos
    ]
    if desconhecidos:
        raise DecisaoInvalida("Há coluna associada a um campo que não existe.")


def _exigir_campos_sem_repeticao(campos: list[str]) -> None:
    repetidos = {campo for campo in campos if campos.count(campo) > 1}
    if repetidos:
        rotulos = ", ".join(sorted(CAMPOS_POR_NOME[c].rotulo for c in repetidos))
        raise DecisaoInvalida(f"Cada campo só pode vir de uma coluna: {rotulos}.")


def _exigir_campos_obrigatorios(campos: list[str], valores_fixos: dict[str, str]) -> None:
    faltando = [
        CAMPOS_POR_NOME[campo].rotulo
        for campo in CAMPOS_OBRIGATORIOS
        if campo not in campos and not valores_fixos.get(campo)
    ]
    if faltando:
        raise DecisaoInvalida(f"Faltam campos obrigatórios: {', '.join(faltando)}.")


def _exigir_fonte(importacao: Importacao, escolha: EscolhaDeColunas, campos: list[str]) -> None:
    if escolha.fonte is None and "fonte" not in campos:
        raise DecisaoInvalida("Escolha de qual fonte é este arquivo.")


@dataclass(frozen=True)
class DefinirColunas:
    servicos: ServicosDeImportacao

    def executar(self, importacao_id: int, escolha: EscolhaDeColunas) -> Importacao:
        importacao = self.servicos.obter(importacao_id)
        importacao.exigir_edicao_aberta()
        mapeamento = self._mapeamento_final(importacao, escolha)
        campos = list(mapeamento.values())
        _exigir_campos_conhecidos(importacao, campos)
        _exigir_campos_sem_repeticao(campos)
        _exigir_campos_obrigatorios(campos, escolha.valores_fixos)
        _exigir_fonte(importacao, escolha, campos)
        if escolha.data_do_retrato > self.servicos.relogio.agora().date():
            raise DecisaoInvalida("A data do retrato não pode estar no futuro.")
        decisoes = replace(
            importacao.decisoes,
            fonte=escolha.fonte,
            data_do_retrato=escolha.data_do_retrato,
            mapeamento=mapeamento,
            valores_fixos=escolha.valores_fixos,
        )
        atualizada = replace(
            importacao,
            status=StatusDaImportacao.VALIDANDO,
            progresso=0,
            decisoes=decisoes,
            fonte=escolha.fonte.value if escolha.fonte else importacao.fonte,
            data_do_retrato=escolha.data_do_retrato,
        )
        self.servicos.importacoes.salvar(atualizada)
        validar = ValidarImportacao(self.servicos)
        self.servicos.fila.enfileirar(lambda: validar.executar(importacao_id))
        return atualizada

    @staticmethod
    def _mapeamento_final(importacao: Importacao, escolha: EscolhaDeColunas) -> dict[str, str]:
        fixas = colunas_com_uso_fixo(importacao)
        combinado = {**escolha.mapeamento, **fixas}
        return {coluna: campo for coluna, campo in combinado.items() if campo}
