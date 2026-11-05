from dataclasses import replace
from datetime import date
from uuid import uuid4

import pytest

from app.application.casos_de_uso.importacoes.cancelar_importacao import CancelarImportacao
from app.application.casos_de_uso.importacoes.confirmar_importacao import ConfirmarImportacao
from app.application.casos_de_uso.importacoes.consultar_importacao import ConsultarImportacao
from app.application.casos_de_uso.importacoes.definir_colunas import (
    DefinirColunas,
    EscolhaDeColunas,
)
from app.application.casos_de_uso.importacoes.desfazer_importacao import DesfazerImportacao
from app.application.casos_de_uso.importacoes.receber_arquivo import ReceberArquivo
from app.application.casos_de_uso.importacoes.responder_pendencias import (
    ResponderPendencias,
    RespostasDePendencias,
)
from app.application.casos_de_uso.importacoes.retomar_importacoes import RetomarImportacoes
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import ArquivoRecebido, ComparacaoComABase
from app.domain.erros import (
    ArquivoVazio,
    DecisaoInvalida,
    ImportacaoEmEstadoInvalido,
    ImportacaoNaoEncontrada,
    ImportacaoNaoPodeSerDesfeita,
)
from app.domain.fontes import Fonte
from app.domain.importacao.datas import FormatoDeData
from app.domain.importacao.decisoes import DEIXAR_VAZIO, PoliticaDeRepetidos
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from tests.fakes_importacao import ARQUIVO, TabelaFalsa, criar_servicos

COLUNAS = [
    "GRUPOSERVICO_DESCRICAO",
    "SERVICO_CODIGO",
    "SERVICO_DESCRICAO",
    "LOGRADOURO",
    "NUMERO",
    "BAIRRO",
    "DATA_DEMANDA",
    "SITUACAO",
    "DATA_ULT_SITUACAO",
]
LINHA = [
    "DRENAGEM",
    "10",
    "Limpeza de canaleta",
    "RUA DO TESTE",
    "10",
    "AFOGADOS",
    "2026-02-10",
    "ATENDIDA",
    "2026-02-12",
]
RETRATO = date(2026, 3, 1)


def servicos_com(linhas: list[list[str]] | None = None) -> ServicosDeImportacao:
    return criar_servicos(TabelaFalsa(COLUNAS, linhas or [LINHA]))


def receber(servicos: ServicosDeImportacao) -> Importacao:
    criada = ReceberArquivo(servicos).executar(ARQUIVO, uuid4())
    return servicos.obter(criada.id)


def escolher_colunas(servicos: ServicosDeImportacao, importacao: Importacao) -> Importacao:
    escolha = EscolhaDeColunas(
        Fonte.CENTRAL_156,
        RETRATO,
        dict(importacao.decisoes.mapeamento),
        dict(importacao.decisoes.valores_fixos),
    )
    DefinirColunas(servicos).executar(importacao.id, escolha)
    return servicos.obter(importacao.id)


def test_arquivo_vazio_e_recusado_e_removido() -> None:
    servicos = servicos_com()
    vazio = ArquivoRecebido("ref", "vazio.csv", 0, "b" * 64)

    with pytest.raises(ArquivoVazio):
        ReceberArquivo(servicos).executar(vazio, uuid4())

    assert servicos.armazenamento.removidos == ["ref"]  # type: ignore[attr-defined]


def test_arquivo_do_portal_e_reconhecido_e_aguarda_as_colunas() -> None:
    importacao = receber(servicos_com())

    assert importacao.status is StatusDaImportacao.AGUARDANDO_COLUNAS
    assert importacao.layout == "portal_156"
    assert importacao.fonte == "156_EMLURB"
    assert importacao.decisoes.mapeamento["GRUPOSERVICO_DESCRICAO"] == "categoria"
    assert importacao.decisoes.valores_fixos["orgao"] == "EMLURB"


def test_analise_nunca_guarda_exemplo_de_coluna_bloqueada() -> None:
    importacao = receber(servicos_com())

    colunas = {coluna["nome"]: coluna for coluna in importacao.estrutura["colunas"]}

    assert colunas["LOGRADOURO"]["bloqueada"] is True
    assert colunas["LOGRADOURO"]["exemplos"] == []
    assert "RUA DO TESTE" not in str(importacao.estrutura)


def test_arquivo_com_dado_pessoal_nao_fica_guardado_depois_da_carga() -> None:
    servicos = servicos_com()
    importacao = escolher_colunas(servicos, receber(servicos))

    ConfirmarImportacao(servicos).executar(importacao.id)

    final = servicos.obter(importacao.id)
    assert final.status is StatusDaImportacao.CONCLUIDA
    assert final.arquivo_guardado is False
    assert servicos.armazenamento.removidos == ["referencia"]  # type: ignore[attr-defined]


def test_definir_colunas_exige_campo_obrigatorio() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)
    mapeamento = {**importacao.decisoes.mapeamento, "DATA_DEMANDA": None}
    escolha = EscolhaDeColunas(Fonte.CENTRAL_156, RETRATO, mapeamento, {})

    with pytest.raises(DecisaoInvalida, match="Data de abertura"):
        DefinirColunas(servicos).executar(importacao.id, escolha)


def test_valor_fixo_supre_campo_obrigatorio() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)
    mapeamento = {**importacao.decisoes.mapeamento, "GRUPOSERVICO_DESCRICAO": None}
    escolha = EscolhaDeColunas(Fonte.CENTRAL_156, RETRATO, mapeamento, {"categoria": "DRENAGEM"})

    DefinirColunas(servicos).executar(importacao.id, escolha)

    assert servicos.obter(importacao.id).status is StatusDaImportacao.PRONTA


def test_duas_colunas_nao_podem_ir_para_o_mesmo_campo() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)
    mapeamento: dict[str, str | None] = {
        **importacao.decisoes.mapeamento,
        "SERVICO_DESCRICAO": "categoria",
    }
    escolha = EscolhaDeColunas(Fonte.CENTRAL_156, RETRATO, mapeamento, {})

    with pytest.raises(DecisaoInvalida, match="Categoria"):
        DefinirColunas(servicos).executar(importacao.id, escolha)


def test_coluna_bloqueada_nao_aceita_outro_destino() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)
    mapeamento: dict[str, str | None] = {
        **importacao.decisoes.mapeamento,
        "LOGRADOURO": "servico",
        "SERVICO_DESCRICAO": None,
    }
    escolha = EscolhaDeColunas(
        Fonte.CENTRAL_156, RETRATO, mapeamento, dict(importacao.decisoes.valores_fixos)
    )

    DefinirColunas(servicos).executar(importacao.id, escolha)

    assert servicos.obter(importacao.id).decisoes.mapeamento["LOGRADOURO"] == "logradouro"


def test_data_do_retrato_nao_pode_estar_no_futuro() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)
    escolha = EscolhaDeColunas(
        Fonte.CENTRAL_156, date(2099, 1, 1), dict(importacao.decisoes.mapeamento), {}
    )

    with pytest.raises(DecisaoInvalida, match="futuro"):
        DefinirColunas(servicos).executar(importacao.id, escolha)


def test_fonte_e_exigida_quando_o_layout_nao_diz() -> None:
    servicos = criar_servicos(TabelaFalsa(["data", "tema"], [["2026-01-01", "X"]]))
    importacao = receber(servicos)
    escolha = EscolhaDeColunas(None, RETRATO, {"data": "data_abertura", "tema": "categoria"}, {})

    with pytest.raises(DecisaoInvalida, match="fonte"):
        DefinirColunas(servicos).executar(importacao.id, escolha)


def test_bairro_desconhecido_vira_pendencia_com_sugestao() -> None:
    linha = [*LINHA]
    linha[5] = "AFOGADOSS"
    servicos = servicos_com([linha])

    importacao = escolher_colunas(servicos, receber(servicos))

    assert importacao.status is StatusDaImportacao.AGUARDANDO_DECISOES
    pendencia = importacao.pendencias["itens"][0]
    assert pendencia["tipo"] == "bairro_desconhecido"
    assert pendencia["valores"][0]["sugestao"] == "AFOGADOS"


def test_responder_a_pendencia_libera_a_importacao() -> None:
    linha = [*LINHA]
    linha[5] = "AFOGADOSS"
    servicos = servicos_com([linha])
    importacao = escolher_colunas(servicos, receber(servicos))

    respostas = RespostasDePendencias(substituicoes={"bairro": {"AFOGADOSS": "AFOGADOS"}})
    ResponderPendencias(servicos).executar(importacao.id, respostas)

    assert servicos.obter(importacao.id).status is StatusDaImportacao.PRONTA


def test_regra_para_os_demais_bairros_resolve_de_uma_vez() -> None:
    linha = [*LINHA]
    linha[5] = "OUTRO LUGAR"
    servicos = servicos_com([linha])
    importacao = escolher_colunas(servicos, receber(servicos))

    respostas = RespostasDePendencias(padrao_para_valores={"bairro": DEIXAR_VAZIO})
    ResponderPendencias(servicos).executar(importacao.id, respostas)

    assert servicos.obter(importacao.id).status is StatusDaImportacao.PRONTA


def test_data_ambigua_vira_pendencia() -> None:
    linha = [*LINHA]
    linha[6], linha[8] = "02/03/2026", ""
    servicos = servicos_com([linha])

    importacao = escolher_colunas(servicos, receber(servicos))

    assert importacao.pendencias["itens"][0]["tipo"] == "formato_de_data"


def test_dia_acima_de_doze_decide_a_data_sem_perguntar() -> None:
    linha = [*LINHA]
    linha[6], linha[8] = "25/03/2026", ""
    servicos = servicos_com([linha])

    importacao = escolher_colunas(servicos, receber(servicos))

    assert importacao.status is StatusDaImportacao.PRONTA
    assert importacao.decisoes.formato_de_data is FormatoDeData.DIA_MES_ANO


def test_linhas_alteradas_na_base_pedem_decisao() -> None:
    servicos = servicos_com()
    servicos.carregador.comparacao = ComparacaoComABase(iguais=0, alteradas=1)  # type: ignore[attr-defined]

    importacao = escolher_colunas(servicos, receber(servicos))

    assert importacao.pendencias["itens"][0]["tipo"] == "repetidos_na_base"

    respostas = RespostasDePendencias(repetidos_na_base=PoliticaDeRepetidos.ATUALIZAR)
    ResponderPendencias(servicos).executar(importacao.id, respostas)
    assert servicos.obter(importacao.id).status is StatusDaImportacao.PRONTA


def test_confirmar_antes_de_resolver_as_pendencias_e_recusado() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)

    with pytest.raises(ImportacaoEmEstadoInvalido):
        ConfirmarImportacao(servicos).executar(importacao.id)


def test_cancelar_remove_o_arquivo() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)

    CancelarImportacao(servicos).executar(importacao.id)

    cancelada = servicos.obter(importacao.id)
    assert cancelada.status is StatusDaImportacao.CANCELADA
    assert cancelada.arquivo_guardado is False
    assert servicos.armazenamento.removidos == ["referencia"]  # type: ignore[attr-defined]


def test_importacao_inexistente_gera_erro_do_dominio() -> None:
    with pytest.raises(ImportacaoNaoEncontrada):
        servicos_com().obter(99)


def concluir(servicos: ServicosDeImportacao) -> Importacao:
    importacao = escolher_colunas(servicos, receber(servicos))
    ConfirmarImportacao(servicos).executar(importacao.id)
    return servicos.obter(importacao.id)


def test_desfazer_a_ultima_importacao_chama_a_base_e_as_views() -> None:
    servicos = servicos_com()
    importacao = concluir(servicos)

    DesfazerImportacao(servicos).executar(importacao.id)

    assert servicos.obter(importacao.id).status is StatusDaImportacao.DESFEITA
    assert servicos.carregador.desfeitas == [importacao.id]  # type: ignore[attr-defined]
    assert servicos.atualizador.chamadas == 2  # type: ignore[attr-defined]


def test_so_a_importacao_mais_recente_pode_ser_desfeita() -> None:
    servicos = servicos_com()
    primeira = concluir(servicos)
    concluir(servicos)

    assert ConsultarImportacao(servicos).executar(primeira.id).pode_desfazer is False
    with pytest.raises(ImportacaoNaoPodeSerDesfeita):
        DesfazerImportacao(servicos).executar(primeira.id)


def test_carga_inicial_nao_pode_ser_desfeita() -> None:
    servicos = servicos_com()
    importacao = concluir(servicos)
    servicos.importacoes.salvar(replace(importacao, carga_inicial=True))
    servicos.importacoes.itens[importacao.id] = replace(  # type: ignore[attr-defined]
        servicos.obter(importacao.id), carga_inicial=True
    )

    with pytest.raises(ImportacaoNaoPodeSerDesfeita):
        DesfazerImportacao(servicos).executar(importacao.id)


def test_ao_subir_a_api_fecha_o_que_ficou_pela_metade() -> None:
    servicos = servicos_com()
    importacao = receber(servicos)
    servicos.importacoes.salvar(importacao.com_status(StatusDaImportacao.ANALISANDO))

    RetomarImportacoes(servicos).executar()

    assert servicos.obter(importacao.id).status is StatusDaImportacao.FALHOU


def test_ao_subir_a_api_retoma_a_atualizacao_das_views() -> None:
    servicos = servicos_com()
    importacao = escolher_colunas(servicos, receber(servicos))
    servicos.importacoes.salvar(importacao.com_status(StatusDaImportacao.ATUALIZANDO_PAINEL))

    RetomarImportacoes(servicos).executar()

    assert servicos.obter(importacao.id).status is StatusDaImportacao.CONCLUIDA
