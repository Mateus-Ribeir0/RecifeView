from collections.abc import Iterable
from datetime import date, timedelta
from typing import cast
from uuid import uuid4

import pytest

from app.application.casos_de_uso.contribuicoes.carregar_logradouros import CarregarLogradouros
from app.application.casos_de_uso.contribuicoes.decidir_par import DecidirPar
from app.application.casos_de_uso.contribuicoes.expurgar_enderecos import ExpurgarEnderecos
from app.application.casos_de_uso.contribuicoes.gerar_pacote import (
    GerarPacote,
    montar_csv_do_pacote,
)
from app.application.casos_de_uso.contribuicoes.receber_contribuicao import ReceberContribuicao
from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.portas.contribuicoes import OcorrenciaDoPacote
from app.domain.contribuicao.comparacao import ClasseDaComparacao, Comparacao
from app.domain.contribuicao.contribuicao import (
    DIAS_DE_GUARDA_DO_ENDERECO,
    DecisaoDoPar,
    FormularioPreenchido,
    ResultadoDoEnvio,
    RetornoAnterior,
)
from app.domain.erros import (
    ContribuicaoInvalida,
    PacoteVazio,
    ParNaoEncontrado,
    PenteFinoPendente,
)
from app.domain.importacao.importacao import StatusDaImportacao
from tests.fakes import INICIO_DOS_TESTES
from tests.fakes_importacao import (
    ContribuicoesEmMemoria,
    ReferenciaFalsa,
    TabelaFalsa,
    criar_servicos,
    criar_servicos_de_contribuicoes,
)

COLUNAS_DO_PACOTE = [
    "CONTRIBUICAO_ID",
    "DATA_ABERTURA",
    "CATEGORIA",
    "SERVICO_CODIGO",
    "SERVICO",
    "BAIRRO_OFICIAL",
    "ID_LOCAL",
    "NUMERO_INFORMADO",
    "RELATOS_SOMADOS",
]


def formulario(chave: str = "a" * 16, **mudancas: str) -> FormularioPreenchido:
    dados: dict[str, object] = {
        "chave_de_envio": chave,
        "servico_codigo": "131",
        "bairro_oficial": "AFOGADOS",
        "logradouro": "R. da Esperança Fictícia",
        "numero": "100",
        "detalhe": "",
        "retorno": RetornoAnterior.NAO_REGISTROU,
        **mudancas,
    }
    return FormularioPreenchido(**dados)  # type: ignore[arg-type]


def ocorrencia() -> OcorrenciaDoPacote:
    return OcorrenciaDoPacote(
        uuid4(),
        date(2026, 3, 10),
        "PAVIMENTACAO",
        "131",
        "OPERACAO TAPA-BURACO",
        "AFOGADOS",
        None,
        True,
        3,
    )


@pytest.fixture
def servicos() -> ServicosDeContribuicoes:
    tabela = TabelaFalsa(COLUNAS_DO_PACOTE, [])
    return criar_servicos_de_contribuicoes(criar_servicos(tabela))


def memoria(servicos: ServicosDeContribuicoes) -> ContribuicoesEmMemoria:
    return cast(ContribuicoesEmMemoria, servicos.contribuicoes)


def test_primeiro_relato_entra_como_novo(servicos: ServicosDeContribuicoes) -> None:
    resultado = ReceberContribuicao(servicos).executar(formulario())

    assert resultado is ResultadoDoEnvio.NOVA
    guardada = memoria(servicos).itens[0]
    assert guardada.logradouro == "RUA DA ESPERANCA FICTICIA"
    assert guardada.categoria == "PAVIMENTACAO"


def test_reenvio_do_mesmo_formulario_nao_conta_duas_vezes(
    servicos: ServicosDeContribuicoes,
) -> None:
    receber = ReceberContribuicao(servicos)

    receber.executar(formulario())
    segundo = receber.executar(formulario())

    assert segundo is ResultadoDoEnvio.NOVA
    assert len(memoria(servicos).itens) == 1


def test_duas_pessoas_com_o_mesmo_relato_viram_uma_ocorrencia(
    servicos: ServicosDeContribuicoes,
) -> None:
    receber = ReceberContribuicao(servicos)

    receber.executar(formulario("a" * 16))
    resultado = receber.executar(formulario("b" * 16, logradouro="Rua da Esperanca Ficticia"))

    assert resultado is ResultadoDoEnvio.SOMADA
    primeira, segunda = memoria(servicos).itens
    assert segunda.principal_id == primeira.id
    assert memoria(servicos).pares == []


def test_relato_parecido_vai_para_o_pente_fino(servicos: ServicosDeContribuicoes) -> None:
    receber = ReceberContribuicao(servicos)

    receber.executar(formulario("a" * 16))
    resultado = receber.executar(formulario("b" * 16, numero="110"))

    assert resultado is ResultadoDoEnvio.EM_CONFERENCIA
    assert len(memoria(servicos).pares) == 1
    assert memoria(servicos).itens[1].principal_id is None


def test_relato_em_outro_endereco_e_outra_ocorrencia(servicos: ServicosDeContribuicoes) -> None:
    receber = ReceberContribuicao(servicos)

    receber.executar(formulario("a" * 16))
    resultado = receber.executar(formulario("b" * 16, logradouro="Rua da Consolação", numero="9"))

    assert resultado is ResultadoDoEnvio.NOVA


def test_com_sal_gera_o_mesmo_pseudonimo_da_importacao() -> None:
    importacao = criar_servicos(TabelaFalsa([], []))
    servicos = criar_servicos_de_contribuicoes(importacao, sal="sal-de-teste")

    ReceberContribuicao(servicos).executar(formulario())

    assert memoria(servicos).itens[0].id_local is not None


@pytest.mark.parametrize(
    "texto",
    [
        "fale comigo no 81 99999-1234",
        "(81) 99999-1234",
        "meu cpf 123.456.789-09",
        "cpf 12345678909",
        "escreva para maria@exemplo.com",
    ],
)
def test_recusa_dado_pessoal_no_detalhe(servicos: ServicosDeContribuicoes, texto: str) -> None:
    with pytest.raises(ContribuicaoInvalida) as erro:
        ReceberContribuicao(servicos).executar(formulario(detalhe=texto))

    assert erro.value.campo == "detalhe"
    assert memoria(servicos).itens == []


def test_aceita_numero_de_imovel_e_referencia_no_detalhe(
    servicos: ServicosDeContribuicoes,
) -> None:
    detalhe = "Em frente ao mercado, perto do número 1200, faz 3 semanas"

    assert ReceberContribuicao(servicos).executar(formulario(detalhe=detalhe))


def test_recusa_servico_e_bairro_fora_da_lista(servicos: ServicosDeContribuicoes) -> None:
    receber = ReceberContribuicao(servicos)

    with pytest.raises(ContribuicaoInvalida):
        receber.executar(formulario(servico_codigo="999"))
    with pytest.raises(ContribuicaoInvalida):
        receber.executar(formulario(bairro_oficial="SAO PAULO"))


def test_decidir_duas_vezes_o_mesmo_par_e_recusado(servicos: ServicosDeContribuicoes) -> None:
    receber = ReceberContribuicao(servicos)
    receber.executar(formulario("a" * 16))
    receber.executar(formulario("b" * 16, numero="110"))
    decidir = DecidirPar(servicos)

    decidir.executar(0, DecisaoDoPar.DIFERENTE, uuid4())

    with pytest.raises(ParNaoEncontrado):
        decidir.executar(0, DecisaoDoPar.MESMA, uuid4())


def test_pacote_nao_sai_com_par_sem_decisao(servicos: ServicosDeContribuicoes) -> None:
    memoria(servicos).prontas = [ocorrencia()]
    memoria(servicos).pares = [
        type("Par", (), {"comparacao": Comparacao(ClasseDaComparacao.PROVAVEL)})()
    ]

    with pytest.raises(PenteFinoPendente):
        GerarPacote(servicos).executar(uuid4())


def test_pacote_vazio_e_recusado(servicos: ServicosDeContribuicoes) -> None:
    with pytest.raises(PacoteVazio):
        GerarPacote(servicos).executar(uuid4())


def test_pacote_entra_no_fluxo_normal_de_importacao() -> None:
    item = ocorrencia()
    linha = [
        str(item.contribuicao_id),
        "2026-03-10",
        "PAVIMENTACAO",
        "131",
        "OPERACAO TAPA-BURACO",
        "AFOGADOS",
        "",
        "SIM",
        "3",
    ]
    servicos = criar_servicos_de_contribuicoes(
        criar_servicos(TabelaFalsa(COLUNAS_DO_PACOTE, [linha]))
    )
    memoria(servicos).prontas = [item]

    importacao = GerarPacote(servicos).executar(uuid4())

    assert memoria(servicos).no_pacote == [item.contribuicao_id]
    final = servicos.importacao.obter(importacao.id)
    assert final.status is StatusDaImportacao.PRONTA
    assert final.layout == "formulario"
    assert final.pendencias["resumo"]["fontes"] == {"FORMULARIO_PUBLICO": 1}


def test_csv_do_pacote_nao_leva_endereco_nem_texto() -> None:
    conteudo = montar_csv_do_pacote([ocorrencia()]).decode()

    assert "LOGRADOURO" not in conteudo
    assert "DETALHE" not in conteudo


def test_expurgo_apaga_depois_do_prazo(servicos: ServicosDeContribuicoes) -> None:
    ExpurgarEnderecos(servicos.contribuicoes, servicos.relogio).executar()

    limite = memoria(servicos).limites_de_expurgo[0]
    assert limite == INICIO_DOS_TESTES - timedelta(days=DIAS_DE_GUARDA_DO_ENDERECO)


def test_lista_de_vias_ignora_via_que_so_apareceu_uma_vez() -> None:
    referencia = ReferenciaFalsa()
    colunas = ["LOGRADOURO", "BAIRRO"]
    linhas = [
        ["RUA DA ESPERANCA", "AFOGADOS"],
        ["RUA DA ESPERANCA", "AFOGADOS"],
        ["RUA ERRADA UMA VEZ", "AFOGADOS"],
        ["RUA DA ESPERANCA", "CIDADE DE FORA"],
    ]
    tabelas: Iterable[TabelaFalsa] = [TabelaFalsa(colunas, linhas)]

    CarregarLogradouros(referencia).executar(tabelas, {"AFOGADOS": "5"})

    assert referencia.somadas == [("AFOGADOS", "RUA DA ESPERANCA", 2)]


def test_data_do_relato_e_o_dia_do_recebimento(servicos: ServicosDeContribuicoes) -> None:
    ReceberContribuicao(servicos).executar(formulario())

    assert memoria(servicos).itens[0].data_relato == INICIO_DOS_TESTES.date()
