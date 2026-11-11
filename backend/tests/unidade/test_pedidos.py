import pytest

from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
)
from app.application.casos_de_uso.pedidos.consultar_pedido import ConsultarPedido
from app.application.casos_de_uso.pedidos.meus_pedidos import (
    AcompanharPedido,
    DeixarDeAcompanhar,
    ListarMeusPedidos,
    ServicosDePedidos,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import LimiteDePedidosAtingido, ProtocoloInvalido
from app.domain.pedido import LIMITE_DE_PEDIDOS_ACOMPANHADOS, RegistroDoPedido
from app.domain.usuario import Perfil
from tests.fakes import (
    ConsultaDePedidosEmMemoria,
    PedidosAcompanhadosEmMemoria,
    RelogioFixo,
    criar_usuario,
)
from tests.fakes_encaminhamento import (
    EncaminhamentosEmMemoria,
    criar_servicos_de_encaminhamento,
    ocorrencia_de_teste,
)

PROTOCOLO = "2026/0001"
REGISTRO = RegistroDoPedido(7, "OUVIDORIA", PROTOCOLO, situacao="EM ANDAMENTO")


def servicos_de_pedidos(
    encaminhamentos: EncaminhamentosEmMemoria | None = None,
) -> ServicosDePedidos:
    consultar = ConsultarPedido(
        ConsultaDePedidosEmMemoria(REGISTRO), encaminhamentos or EncaminhamentosEmMemoria()
    )
    return ServicosDePedidos(consultar, PedidosAcompanhadosEmMemoria(), RelogioFixo())


def test_consulta_acha_o_pedido_digitado_com_espacos_e_minusculas() -> None:
    andamentos = servicos_de_pedidos().consultar.executar(" 2026 / 0001 ")

    assert [andamento.registro.chave_registro for andamento in andamentos] == [7]


def test_consulta_mostra_para_qual_orgao_o_pedido_foi_encaminhado() -> None:
    encaminhamentos = EncaminhamentosEmMemoria(ocorrencia_de_teste(7))
    servicos = criar_servicos_de_encaminhamento(encaminhamentos)
    EncaminharOcorrencia(servicos).executar(PedidoDeEncaminhamento(7, Orgao.COMPESA))

    (andamento,) = servicos_de_pedidos(encaminhamentos).consultar.executar(PROTOCOLO)

    assert [item.orgao for item in andamento.encaminhamentos] == [Orgao.COMPESA]


def test_consulta_recusa_texto_que_nao_e_protocolo() -> None:
    with pytest.raises(ProtocoloInvalido):
        servicos_de_pedidos().consultar.executar("Rua do Sol, 10")


def test_cidadao_guarda_o_mesmo_protocolo_uma_vez_so() -> None:
    servicos, cidadao = servicos_de_pedidos(), criar_usuario(perfil=Perfil.CIDADAO)

    AcompanharPedido(servicos).executar(cidadao, PROTOCOLO)
    AcompanharPedido(servicos).executar(cidadao, "2026/0001")
    pedidos = ListarMeusPedidos(servicos).executar(cidadao)

    assert len(pedidos) == 1
    assert pedidos[0].andamentos[0].registro.situacao == "EM ANDAMENTO"


def test_protocolo_ainda_sem_registro_fica_guardado_sem_andamento() -> None:
    servicos, cidadao = servicos_de_pedidos(), criar_usuario(perfil=Perfil.CIDADAO)

    pedido = AcompanharPedido(servicos).executar(cidadao, "2026/9999")

    assert pedido.andamentos == []


def test_cidadao_acompanha_no_maximo_vinte_pedidos() -> None:
    servicos, cidadao = servicos_de_pedidos(), criar_usuario(perfil=Perfil.CIDADAO)
    for numero in range(LIMITE_DE_PEDIDOS_ACOMPANHADOS):
        AcompanharPedido(servicos).executar(cidadao, f"2026/{numero:04d}X")

    with pytest.raises(LimiteDePedidosAtingido):
        AcompanharPedido(servicos).executar(cidadao, "2026/NOVO")


def test_deixar_de_acompanhar_so_tira_o_pedido_da_propria_conta() -> None:
    servicos = servicos_de_pedidos()
    dona, outra = criar_usuario(perfil=Perfil.CIDADAO), criar_usuario(perfil=Perfil.CIDADAO)
    pedido = AcompanharPedido(servicos).executar(dona, PROTOCOLO)

    DeixarDeAcompanhar(servicos).executar(outra, pedido.pedido.id)
    assert len(ListarMeusPedidos(servicos).executar(dona)) == 1
    DeixarDeAcompanhar(servicos).executar(dona, pedido.pedido.id)
    assert ListarMeusPedidos(servicos).executar(dona) == []
