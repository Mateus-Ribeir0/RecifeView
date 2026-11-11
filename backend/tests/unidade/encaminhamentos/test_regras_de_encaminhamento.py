from datetime import UTC, date, datetime

import pytest

from app.domain.encaminhamento.encaminhamento import (
    CanalDeEnvio,
    Encaminhamento,
    SituacaoDoEncaminhamento,
    calcular_prazo_de_resposta,
    exigir_transicao,
    limpar_texto_curto,
    tem_encaminhamento_aberto,
)
from app.domain.encaminhamento.mensagem import montar_mensagem
from app.domain.encaminhamento.orgaos import Orgao, orgao_da_fonte
from app.domain.encaminhamento.sugestao import (
    INDICACOES_MINIMAS_PARA_SUGERIR,
    CitacoesDoTema,
    MotivoDaSugestao,
    medir_participacoes,
    sugerir_destino,
    tema_na_camara,
)
from app.domain.erros import EncaminhamentoInvalido, TransicaoInvalida
from tests.fakes_encaminhamento import ocorrencia_de_teste

CRIADO_EM = datetime(2026, 11, 11, 15, 0, tzinfo=UTC)
DRENAGEM = CitacoesDoTema(
    "DRENAGEM", 100, {"EMLURB": 80, "SEINFRA/INFRAESTRUTURA": 9, "COMPESA": 1, "PREFEITO": 5}
)


def encaminhamento_de_teste(**alteracoes: object) -> Encaminhamento:
    valores: dict[str, object] = {
        "id": 42,
        "ocorrencia": ocorrencia_de_teste(protocolo="2026/OUV-7"),
        "orgao": Orgao.COMPESA,
        "orgao_sugerido": Orgao.EMLURB,
        "canal": CanalDeEnvio.LOCAL,
        "situacao": SituacaoDoEncaminhamento.ENVIADO,
        "criado_em": CRIADO_EM,
        "prazo_de_resposta": calcular_prazo_de_resposta(CRIADO_EM.date()),
        "atualizado_em": CRIADO_EM,
        "nota": 8.25,
    }
    return Encaminhamento(**(valores | alteracoes))  # type: ignore[arg-type]


def test_registro_que_aponta_um_orgao_do_catalogo_define_a_sugestao() -> None:
    sugestao = sugerir_destino("COMPESA", DRENAGEM)

    assert sugestao.orgao is Orgao.COMPESA
    assert sugestao.motivo is MotivoDaSugestao.APONTADO_NO_REGISTRO


def test_sem_orgao_no_registro_sugere_o_mais_citado_no_tema() -> None:
    sugestao = sugerir_destino(None, DRENAGEM)

    assert sugestao.orgao is Orgao.EMLURB
    assert sugestao.motivo is MotivoDaSugestao.MAIS_CITADO_NO_TEMA


def test_tema_com_poucas_indicacoes_nao_gera_sugestao() -> None:
    poucas = CitacoesDoTema("PRACAS", INDICACOES_MINIMAS_PARA_SUGERIR - 1, {"EMLURB": 20})

    sugestao = sugerir_destino("PREFEITO", poucas)

    assert sugestao.orgao is None
    assert sugestao.motivo is MotivoDaSugestao.SEM_SUGESTAO
    assert sugestao.participacoes


def test_participacao_conta_sobre_todas_as_indicacoes_do_tema() -> None:
    participacoes = medir_participacoes(DRENAGEM)

    assert [item.orgao for item in participacoes] == [Orgao.EMLURB, Orgao.SEINFRA, Orgao.COMPESA]
    assert participacoes[0].pct == pytest.approx(80.0)
    assert participacoes[2].pct == pytest.approx(1.0)


def test_categoria_do_156_sem_tema_na_camara_cai_no_tema_mais_proximo() -> None:
    assert tema_na_camara("LUMINARIAS") == "ILUMINACAO PUBLICA"
    assert tema_na_camara("DRENAGEM") == "DRENAGEM"
    assert tema_na_camara(None) is None


def test_nome_do_orgao_na_ouvidoria_e_na_camara_vira_o_mesmo_orgao() -> None:
    assert orgao_da_fonte("SECRETARIA DE SAUDE") is Orgao.SAUDE
    assert orgao_da_fonte(" saude ") is Orgao.SAUDE
    assert orgao_da_fonte("PREFEITO") is None


@pytest.mark.parametrize(
    ("atual", "nova"),
    [
        (SituacaoDoEncaminhamento.RESOLVIDO, SituacaoDoEncaminhamento.RECEBIDO),
        (SituacaoDoEncaminhamento.RECEBIDO, SituacaoDoEncaminhamento.RECEBIDO),
        (SituacaoDoEncaminhamento.ENVIADO, SituacaoDoEncaminhamento.FALHOU),
        (SituacaoDoEncaminhamento.DEVOLVIDO, SituacaoDoEncaminhamento.ENVIADO),
    ],
)
def test_ciclo_recusa_resposta_fora_de_ordem(
    atual: SituacaoDoEncaminhamento, nova: SituacaoDoEncaminhamento
) -> None:
    with pytest.raises(TransicaoInvalida):
        exigir_transicao(atual, nova)


def test_falha_do_canal_pode_ser_reenviada() -> None:
    exigir_transicao(SituacaoDoEncaminhamento.FALHOU, SituacaoDoEncaminhamento.ENVIADO)


def test_encaminhamento_aberto_depois_do_prazo_fica_atrasado() -> None:
    encaminhamento = encaminhamento_de_teste()
    depois_do_prazo = date(2026, 12, 12)

    assert encaminhamento.prazo_de_resposta == date(2026, 12, 11)
    assert encaminhamento.esta_atrasado(depois_do_prazo)
    resolvido = encaminhamento_de_teste(situacao=SituacaoDoEncaminhamento.RESOLVIDO)
    assert not resolvido.esta_atrasado(depois_do_prazo)


def test_devolvido_libera_a_ocorrencia_para_outro_orgao() -> None:
    devolvido = encaminhamento_de_teste(situacao=SituacaoDoEncaminhamento.DEVOLVIDO)

    assert not tem_encaminhamento_aberto([devolvido])
    assert tem_encaminhamento_aberto([devolvido, encaminhamento_de_teste()])


def test_codigo_tem_ano_e_numero_com_seis_digitos() -> None:
    assert encaminhamento_de_teste().codigo == "ENC-2026-000042"


def test_texto_curto_recusa_contato_pessoal_e_excesso() -> None:
    with pytest.raises(EncaminhamentoInvalido):
        limpar_texto_curto("observacao", "Ligue para (81) 99999-1234", 280)
    with pytest.raises(EncaminhamentoInvalido):
        limpar_texto_curto("observacao", "x" * 281, 280)
    assert limpar_texto_curto("observacao", "   ", 280) is None


def test_mensagem_leva_protocolo_de_origem_prazo_e_link() -> None:
    link = "https://recifeview.exemplo/retorno/abc"

    mensagem = montar_mensagem(encaminhamento_de_teste(), link, date(2027, 1, 10))

    assert mensagem.orgao is Orgao.COMPESA
    assert "Protocolo de origem: 2026/OUV-7" in mensagem.corpo
    assert "11/12/2026" in mensagem.corpo
    assert "Nota de prioridade: 8,2 de 10" in mensagem.corpo
    assert mensagem.corpo.endswith(link)
    assert mensagem.dados["link_de_retorno"] == link
