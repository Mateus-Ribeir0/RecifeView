from datetime import date, timedelta
from uuid import uuid4

import pytest

from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
    PrepararEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.encaminhar_prioritarias import (
    EncaminharPrioritarias,
    MotivoParaPular,
    PedidoAutomatico,
)
from app.application.casos_de_uso.encaminhamentos.retorno import (
    AbrirPeloLink,
    ReenviarEncaminhamento,
    RegistrarRetornoPelaGestao,
    RegistrarRetornoPeloLink,
    RespostaAoEncaminhamento,
)
from app.domain.encaminhamento.encaminhamento import (
    VALIDADE_DO_LINK_DE_RETORNO,
    AutorDoEvento,
    CanalDeEnvio,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.encaminhamento.sugestao import CitacoesDoTema
from app.domain.erros import (
    LinkDeRetornoInvalido,
    OcorrenciaJaEncaminhada,
    OcorrenciaNaoEncontrada,
    TransicaoInvalida,
)
from app.domain.prioridade import FonteDaFila, Ocorrencia
from tests.fakes import RelogioFixo
from tests.fakes_encaminhamento import (
    ENDERECO_DO_SITE,
    DespachoEmMemoria,
    EncaminhamentosEmMemoria,
    PrioridadeFalsa,
    criar_servicos_de_encaminhamento,
    ocorrencia_de_teste,
)

RESOLVIDO = RespostaAoEncaminhamento(SituacaoDoEncaminhamento.RESOLVIDO, " CMP 123 ", "Feito.")
PRAZO_TIPICO_DA_FILA = 100


def fila_em_ordem(chaves: tuple[int, ...]) -> PrioridadeFalsa:
    """Cada chave está mais atrasada que a seguinte, então a fila sai na ordem das chaves."""
    return PrioridadeFalsa(
        [
            Ocorrencia(
                data_abertura=date(2026, 1, 1),
                idade_dias=PRAZO_TIPICO_DA_FILA - (posicao + 1) * 10,
                prazo_tipico_dias=PRAZO_TIPICO_DA_FILA,
                pedidos_anteriores=0,
                bairro_oficial="AFOGADOS",
                chave_registro=chave,
            )
            for posicao, chave in enumerate(chaves)
        ]
    )


def encaminhar_compesa(
    repositorio: EncaminhamentosEmMemoria, despacho: DespachoEmMemoria, chave: int = 1
) -> None:
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho)
    EncaminharOcorrencia(servicos).executar(PedidoDeEncaminhamento(chave, Orgao.COMPESA))


def test_preparo_traz_sugestao_canais_e_historico() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste(orgao=None))
    repositorio.citacoes["DRENAGEM"] = CitacoesDoTema("DRENAGEM", 40, {"EMLURB": 35})
    despacho = DespachoEmMemoria(canais={Orgao.COMPESA: CanalDeEnvio.EMAIL})
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho)

    preparo = PrepararEncaminhamento(servicos).executar(1)

    assert preparo.sugestao.orgao is Orgao.EMLURB
    assert preparo.canais[Orgao.COMPESA] is CanalDeEnvio.EMAIL
    assert preparo.canais[Orgao.CTTU] is CanalDeEnvio.LOCAL
    assert preparo.pode_encaminhar


def test_ocorrencia_que_saiu_da_base_nao_pode_ser_encaminhada() -> None:
    servicos = criar_servicos_de_encaminhamento(EncaminhamentosEmMemoria())

    with pytest.raises(OcorrenciaNaoEncontrada):
        PrepararEncaminhamento(servicos).executar(99)


def test_encaminhar_grava_com_a_sugestao_e_manda_pelo_canal_do_orgao() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    despacho = DespachoEmMemoria()
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho)
    gestor = uuid4()

    encaminhamento = EncaminharOcorrencia(servicos).executar(
        PedidoDeEncaminhamento(1, Orgao.COMPESA, gestor, " Vazamento recorrente ", 8.4)
    )

    assert encaminhamento.situacao is SituacaoDoEncaminhamento.ENVIADO
    assert encaminhamento.orgao_sugerido is Orgao.EMLURB
    assert encaminhamento.justificativa == "Vazamento recorrente"
    assert encaminhamento.prazo_de_resposta == date(2026, 11, 25)
    assert despacho.enviadas[0].orgao is Orgao.COMPESA
    assert str(despacho.enviadas[0].dados["link_de_retorno"]).startswith(ENDERECO_DO_SITE)


def test_canal_que_falha_deixa_o_encaminhamento_gravado_como_falha() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    servicos = criar_servicos_de_encaminhamento(repositorio, DespachoEmMemoria(falhar=True))

    encaminhamento = EncaminharOcorrencia(servicos).executar(
        PedidoDeEncaminhamento(1, Orgao.COMPESA)
    )

    assert encaminhamento.situacao is SituacaoDoEncaminhamento.FALHOU
    assert encaminhamento.eventos[-1].autor is AutorDoEvento.SISTEMA


def test_ocorrencia_com_encaminhamento_aberto_nao_segue_de_novo() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    despacho = DespachoEmMemoria()
    encaminhar_compesa(repositorio, despacho)

    with pytest.raises(OcorrenciaJaEncaminhada):
        encaminhar_compesa(repositorio, despacho)


def test_orgao_responde_pelo_link_e_o_ciclo_avanca() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    despacho = DespachoEmMemoria()
    encaminhar_compesa(repositorio, despacho)
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho)

    resolvido = RegistrarRetornoPeloLink(servicos).executar(despacho.ultimo_token(), RESOLVIDO)

    assert resolvido.situacao is SituacaoDoEncaminhamento.RESOLVIDO
    assert resolvido.protocolo_do_orgao == "CMP 123"
    assert resolvido.eventos[-1].autor is AutorDoEvento.ORGAO
    with pytest.raises(TransicaoInvalida):
        RegistrarRetornoPeloLink(servicos).executar(despacho.ultimo_token(), RESOLVIDO)


def test_link_vencido_nao_abre() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    despacho = DespachoEmMemoria()
    relogio = RelogioFixo()
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho, relogio)
    EncaminharOcorrencia(servicos).executar(PedidoDeEncaminhamento(1, Orgao.COMPESA))
    relogio.avancar(VALIDADE_DO_LINK_DE_RETORNO + timedelta(minutes=1))

    with pytest.raises(LinkDeRetornoInvalido):
        AbrirPeloLink(servicos).executar(despacho.ultimo_token())


def test_gestao_registra_o_retorno_recebido_por_telefone() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    encaminhar_compesa(repositorio, DespachoEmMemoria())
    servicos = criar_servicos_de_encaminhamento(repositorio)
    gestor = uuid4()
    recebido = RespostaAoEncaminhamento(SituacaoDoEncaminhamento.RECEBIDO)

    encaminhamento = RegistrarRetornoPelaGestao(servicos).executar(1, recebido, gestor)

    assert encaminhamento.situacao is SituacaoDoEncaminhamento.RECEBIDO
    assert encaminhamento.eventos[-1].autor is AutorDoEvento.GESTAO


def test_reenvio_depois_da_falha_troca_o_link() -> None:
    repositorio = EncaminhamentosEmMemoria(ocorrencia_de_teste())
    despacho = DespachoEmMemoria(falhar=True)
    encaminhar_compesa(repositorio, despacho)
    despacho.falhar = False
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho)

    reenviado = ReenviarEncaminhamento(servicos).executar(1, uuid4())

    assert reenviado.situacao is SituacaoDoEncaminhamento.ENVIADO
    assert len(despacho.enviadas) == 1
    assert AbrirPeloLink(servicos).executar(despacho.ultimo_token()).id == 1


def test_envio_automatico_segue_a_fila_e_pula_o_que_ja_foi_encaminhado() -> None:
    chaves = (1, 2, 3)
    repositorio = EncaminhamentosEmMemoria(*(ocorrencia_de_teste(chave) for chave in chaves))
    repositorio.ocorrencias[3] = ocorrencia_de_teste(3, orgao=None, categoria=None)
    despacho = DespachoEmMemoria()
    encaminhar_compesa(repositorio, despacho, chave=2)
    fila = fila_em_ordem(chaves)
    servicos = criar_servicos_de_encaminhamento(repositorio, despacho)

    resultado = EncaminharPrioritarias(servicos, fila).executar(
        PedidoAutomatico(FonteDaFila.CENTRAL_156, nota_minima=0)
    )

    assert resultado.candidatas == 3
    assert [item.ocorrencia.chave_registro for item in resultado.encaminhadas] == [1]
    assert resultado.encaminhadas[0].automatico
    assert resultado.encaminhadas[0].orgao is Orgao.EMLURB
    assert resultado.puladas[MotivoParaPular.JA_ENCAMINHADA] == 1
    assert resultado.puladas[MotivoParaPular.SEM_SUGESTAO] == 1


def test_envio_automatico_respeita_o_limite_por_execucao() -> None:
    chaves = (1, 2, 3)
    repositorio = EncaminhamentosEmMemoria(*(ocorrencia_de_teste(chave) for chave in chaves))
    servicos = criar_servicos_de_encaminhamento(repositorio)

    resultado = EncaminharPrioritarias(servicos, fila_em_ordem(chaves)).executar(
        PedidoAutomatico(FonteDaFila.CENTRAL_156, nota_minima=0, limite=2)
    )

    assert len(resultado.encaminhadas) == 2
