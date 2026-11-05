import re

from app.domain.fontes import Iniciativa
from app.domain.importacao.layouts import (
    AUXILIAR_DATA_DA_ACAO,
    AUXILIAR_GRAU_DE_RISCO,
    AUXILIAR_MES,
    AUXILIAR_OCORRENCIA,
    AUXILIAR_REGIONAL,
    AUXILIAR_SOLICITACAO,
    AUXILIAR_TIPO_DA_ACAO,
    ENDERECO,
)

PADRAO_ANO = re.compile(r"\d{4}")
PADRAO_GRAU_DE_RISCO = re.compile(r"R[1-4]")

CLASSE_MONITORAMENTO = "MONITORAMENTO (proativo)"
CLASSE_LONA = "LONA (demanda)"
CLASSE_VISTORIA = "VISTORIA (demanda)"
CLASSE_SEM_REGISTRO = "SEM REGISTRO"
CLASSE_OUTRA = "OUTRO"


def classificar_solicitacao(solicitacao: str) -> str:
    if solicitacao.startswith("MONITORAMENTO"):
        return CLASSE_MONITORAMENTO
    if "LONA" in solicitacao:
        return CLASSE_LONA
    if "VISTORIA" in solicitacao:
        return CLASSE_VISTORIA
    return CLASSE_SEM_REGISTRO if not solicitacao else CLASSE_OUTRA


def iniciativa_da_classe(classe: str) -> Iniciativa:
    if classe.startswith("MONITOR"):
        return Iniciativa.PROATIVA
    return Iniciativa.CIDADAO if "(demanda)" in classe else Iniciativa.INDEFINIDA


def _corrigir_colunas_deslocadas(valores: dict[str, str]) -> None:
    # Em 2015, 2019, 2020 e 2022 a coluna Regional sumiu e o endereço foi partido em dois:
    # cada valor ficou uma coluna à esquerda do cabeçalho.
    if not PADRAO_ANO.fullmatch(valores.get(AUXILIAR_REGIONAL, "")):
        return
    ocorrencia = valores.get("data_abertura", "")
    solicitacao = valores.get(AUXILIAR_OCORRENCIA, "")
    endereco = valores.get(AUXILIAR_SOLICITACAO, "")
    valores["ano"] = valores.get(AUXILIAR_REGIONAL, "")
    valores["data_abertura"] = valores.get(AUXILIAR_MES, "")
    valores[AUXILIAR_OCORRENCIA] = ocorrencia
    valores[AUXILIAR_SOLICITACAO] = solicitacao
    valores[ENDERECO] = endereco


def adaptar_linha_da_defesa_civil(valores: dict[str, str]) -> None:
    _corrigir_colunas_deslocadas(valores)
    solicitacao = valores.get(AUXILIAR_SOLICITACAO, "")
    classe = classificar_solicitacao(solicitacao)
    grau = PADRAO_GRAU_DE_RISCO.search(valores.get(AUXILIAR_GRAU_DE_RISCO, "").replace(" ", ""))
    data_da_acao = valores.get(AUXILIAR_DATA_DA_ACAO, "")
    valores["categoria"] = classe
    valores["servico"] = solicitacao
    valores["iniciativa"] = iniciativa_da_classe(classe).value
    valores["situacao"] = grau.group() if grau else ""
    valores["tipo_registro"] = f"ACAO: {valores.get(AUXILIAR_TIPO_DA_ACAO, '')}"
    valores["data_ult_movimento"] = data_da_acao
    valores["data_abertura"] = valores.get("data_abertura") or data_da_acao
    valores[ENDERECO] = valores.get(ENDERECO, "").split(",")[0]
