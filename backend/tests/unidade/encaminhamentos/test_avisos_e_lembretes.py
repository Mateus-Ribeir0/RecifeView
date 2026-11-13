from datetime import date, timedelta
from uuid import uuid4

import pytest

from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.lembrete import LembrarOrgaos
from app.application.casos_de_uso.encaminhamentos.pendencias import ConsultarPendenciasDoPainel
from app.application.casos_de_uso.encaminhamentos.retorno import (
    AbrirPeloLink,
    ReenviarEncaminhamento,
    RegistrarRetornoPelaGestao,
    RegistrarRetornoPeloLink,
    RespostaAoEncaminhamento,
)
from app.domain.contribuicao.conferencia import chave_da_contribuicao
from app.domain.encaminhamento.encaminhamento import (
    DIAS_PARA_O_ORGAO_RESPONDER,
    SituacaoDoEncaminhamento,
    descrever_local_aproximado,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import EncaminhamentoInvalido
from app.domain.fontes import Fonte
from tests.fakes_encaminhamento import Ambiente, EncaminhamentosEmMemoria, ocorrencia_de_teste

GESTORA = "gestora@exemplo.gov.br"
MORADORA = "moradora@exemplo.com"
RESOLVIDO = RespostaAoEncaminhamento(
    SituacaoDoEncaminhamento.RESOLVIDO, "CMP-1", "Equipe foi ao local"
)
PRAZO_VENCIDO = timedelta(days=DIAS_PARA_O_ORGAO_RESPONDER + 1)


def ambiente_com_ocorrencia() -> Ambiente:
    ambiente = Ambiente(EncaminhamentosEmMemoria(ocorrencia_de_teste(protocolo="TESTE-1")))
    ambiente.destinatarios.quem_encaminhou = GESTORA
    ambiente.destinatarios.quem_acompanha = [MORADORA]
    return ambiente


def encaminhar(ambiente: Ambiente) -> None:
    pedido = PedidoDeEncaminhamento(1, Orgao.COMPESA, uuid4(), "Ponto crônico")
    EncaminharOcorrencia(ambiente.servicos()).executar(pedido)


def test_envio_avisa_quem_acompanha_o_pedido() -> None:
    ambiente = ambiente_com_ocorrencia()

    encaminhar(ambiente)

    (aviso,) = ambiente.entrega.para(MORADORA)
    assert "protocolo TESTE-1 foi encaminhado para Compesa" in aviso.corpo
    assert "/cidade/meus-pedidos" in aviso.corpo
    assert ambiente.entrega.para(GESTORA) == []


def test_envio_que_falha_nao_avisa_ninguem_e_o_reenvio_avisa() -> None:
    ambiente = ambiente_com_ocorrencia()
    ambiente.despacho.falhar = True
    encaminhar(ambiente)

    assert ambiente.entrega.entregues == []
    ambiente.despacho.falhar = False
    ReenviarEncaminhamento(ambiente.servicos()).executar(1, uuid4())
    assert len(ambiente.entrega.para(MORADORA)) == 1


def test_resposta_do_orgao_avisa_quem_encaminhou_e_quem_acompanha() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)

    RegistrarRetornoPeloLink(ambiente.servicos()).executar(
        ambiente.despacho.ultimo_token(), RESOLVIDO
    )

    (aviso_da_gestao,) = ambiente.entrega.para(GESTORA)
    assert "Compesa informou que resolveu" in aviso_da_gestao.corpo
    assert "Protocolo no órgão: CMP-1" in aviso_da_gestao.corpo
    assert "Equipe foi ao local" in aviso_da_gestao.corpo
    assert "/painel/encaminhamentos/1" in aviso_da_gestao.corpo
    ultimo_da_moradora = ambiente.entrega.para(MORADORA)[-1]
    assert "foi resolvido, segundo Compesa" in ultimo_da_moradora.corpo


def test_aviso_ao_cidadao_nao_leva_texto_da_gestao_nem_do_orgao() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)

    RegistrarRetornoPeloLink(ambiente.servicos()).executar(
        ambiente.despacho.ultimo_token(), RESOLVIDO
    )

    for aviso in ambiente.entrega.para(MORADORA):
        assert "Ponto crônico" not in aviso.corpo
        assert "Equipe foi ao local" not in aviso.corpo
        assert "CMP-1" not in aviso.corpo


def test_retorno_registrado_pela_gestao_nao_volta_para_a_gestao() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)

    RegistrarRetornoPelaGestao(ambiente.servicos()).executar(1, RESOLVIDO, uuid4())

    assert ambiente.entrega.para(GESTORA) == []
    assert len(ambiente.entrega.para(MORADORA)) == 2


def test_prazo_vencido_gera_um_lembrete_com_link_novo() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)
    link_original = ambiente.despacho.ultimo_token()
    ambiente.relogio.avancar(PRAZO_VENCIDO)

    primeira = LembrarOrgaos(ambiente.servicos()).executar()
    segunda = LembrarOrgaos(ambiente.servicos()).executar()

    assert (primeira.enviados, segunda.enviados) == (1, 0)
    lembrete = ambiente.despacho.enviadas[-1]
    assert lembrete.assunto.startswith("Lembrete")
    assert "Este link substitui o da mensagem anterior" in lembrete.corpo
    assert AbrirPeloLink(ambiente.servicos()).executar(ambiente.despacho.ultimo_token()).id == 1
    assert ambiente.despacho.ultimo_token() != link_original


def test_lembrete_que_falha_no_canal_fica_para_a_proxima_vez() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)
    ambiente.relogio.avancar(PRAZO_VENCIDO)
    ambiente.despacho.falhar = True

    resultado = LembrarOrgaos(ambiente.servicos()).executar()

    assert (resultado.enviados, resultado.falhas) == (0, 1)
    assert ambiente.repositorio.vencidos_sem_lembrete(ambiente.relogio.agora().date())


def test_relato_encaminhado_leva_a_rua_oficial_e_a_faixa() -> None:
    relato = uuid4()
    chave = chave_da_contribuicao(relato)
    repositorio = EncaminhamentosEmMemoria(
        ocorrencia_de_teste(chave, fonte=Fonte.FORMULARIO.value, protocolo=None)
    )
    repositorio.locais_dos_relatos[relato] = "RUA DA AURORA, entre 100 e 199"
    ambiente = Ambiente(repositorio)

    pedido = PedidoDeEncaminhamento(chave, Orgao.EMLURB, contribuicao_id=relato)
    encaminhamento = EncaminharOcorrencia(ambiente.servicos()).executar(pedido)

    assert encaminhamento.contribuicao_id == relato
    assert "Local aproximado: RUA DA AURORA, entre 100 e 199" in ambiente.despacho.enviadas[0].corpo


def test_aviso_de_relato_aponta_para_meus_relatos() -> None:
    relato = uuid4()
    chave = chave_da_contribuicao(relato)
    repositorio = EncaminhamentosEmMemoria(
        ocorrencia_de_teste(chave, fonte=Fonte.FORMULARIO.value, protocolo=None)
    )
    ambiente = Ambiente(repositorio)
    ambiente.destinatarios.quem_acompanha = [MORADORA]

    pedido = PedidoDeEncaminhamento(chave, Orgao.EMLURB, contribuicao_id=relato)
    EncaminharOcorrencia(ambiente.servicos()).executar(pedido)

    (aviso,) = ambiente.entrega.para(MORADORA)
    assert aviso.corpo.startswith("O problema que você relatou foi encaminhado para Emlurb")
    assert "/cidade/meus-relatos" in aviso.corpo


def test_relato_de_outra_ocorrencia_e_recusado() -> None:
    ambiente = Ambiente(EncaminhamentosEmMemoria(ocorrencia_de_teste(1)))

    with pytest.raises(EncaminhamentoInvalido):
        EncaminharOcorrencia(ambiente.servicos()).executar(
            PedidoDeEncaminhamento(1, Orgao.EMLURB, contribuicao_id=uuid4())
        )


class DuplasFalsas:
    def contar_pares_abertos(self) -> int:
        return 2


def test_pendencias_contam_devolucao_ate_a_ocorrencia_seguir_adiante() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)
    devolvido = RespostaAoEncaminhamento(SituacaoDoEncaminhamento.DEVOLVIDO)
    RegistrarRetornoPelaGestao(ambiente.servicos()).executar(1, devolvido, uuid4())
    consulta = ConsultarPendenciasDoPainel(ambiente.repositorio, DuplasFalsas(), ambiente.relogio)

    antes = consulta.executar()
    encaminhar(ambiente)
    depois = consulta.executar()

    assert (antes.encaminhamentos.devolvidos, antes.duplas_no_pente_fino) == (1, 2)
    assert depois.encaminhamentos.pedem_acao == 0


def test_local_aproximado_so_tem_rua_oficial_e_faixa() -> None:
    assert descrever_local_aproximado("RUA DO SOL", "245") == "RUA DO SOL, entre 200 e 299"
    assert descrever_local_aproximado("RUA DO SOL", "S/N") == "RUA DO SOL"
    assert descrever_local_aproximado(None, "245") is None


def test_lembrete_traz_o_prazo_que_venceu() -> None:
    ambiente = ambiente_com_ocorrencia()
    encaminhar(ambiente)
    ambiente.relogio.avancar(PRAZO_VENCIDO)

    LembrarOrgaos(ambiente.servicos()).executar()

    prazo = (date(2026, 10, 26) + timedelta(days=DIAS_PARA_O_ORGAO_RESPONDER)).strftime("%d/%m/%Y")
    assert f"o prazo de {prazo}" in ambiente.despacho.enviadas[-1].corpo
