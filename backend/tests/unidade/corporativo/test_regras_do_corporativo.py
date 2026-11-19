from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.acesso_corporativo import AcessoCorporativo, ConviteDeAcesso, SituacaoDoAcesso
from app.domain.contribuicao.comparacao import ClasseDaComparacao
from app.domain.encaminhamento.avisos import (
    aviso_ao_cidadao,
    aviso_de_nova_ocorrencia,
    aviso_de_prazo_vencido,
)
from app.domain.encaminhamento.desempenho import IndicadoresDoOrgao
from app.domain.encaminhamento.encaminhamento import (
    AutorDoEvento,
    CanalDeEnvio,
    Encaminhamento,
    EventoDoEncaminhamento,
    SituacaoDoEncaminhamento,
    exigir_previsao_valida,
)
from app.domain.encaminhamento.mesmo_problema import (
    agrupar_mesmo_problema,
    comparar_ocorrencias,
    encontrar_mesmo_problema,
)
from app.domain.encaminhamento.orgaos import Orgao, nomes_na_fonte
from app.domain.erros import EncaminhamentoInvalido
from app.domain.fontes import Fonte
from app.domain.usuario import Perfil, email_da_conta_excluida
from tests.fakes import criar_usuario
from tests.fakes_encaminhamento import ENDERECO_DO_SITE, ocorrencia_de_teste

AGORA = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)
HOJE = AGORA.date()
NO_MESMO_LOCAL = {"id_local": "local-1", "numero_informado": True, "servico_codigo": "S1"}


def encaminhamento_de_teste(identificador: int, **ocorrencia: object) -> Encaminhamento:
    return Encaminhamento(
        id=identificador,
        ocorrencia=ocorrencia_de_teste(identificador, **ocorrencia),
        orgao=Orgao.EMLURB,
        orgao_sugerido=None,
        canal=CanalDeEnvio.LOCAL,
        situacao=SituacaoDoEncaminhamento.ENVIADO,
        criado_em=AGORA,
        prazo_de_resposta=date(2026, 12, 19),
        atualizado_em=AGORA,
    )


def acesso(**alteracoes: object) -> AcessoCorporativo:
    base = AcessoCorporativo(
        usuario_id=uuid4(),
        nome="Pessoa",
        email="pessoa@orgao.exemplo",
        orgao=Orgao.COMPESA,
        ativo=True,
        criado_em=AGORA,
        convite_aceito=False,
        convite_expira_em=AGORA + timedelta(days=7),
    )
    return replace(base, **alteracoes)  # type: ignore[arg-type]


def test_conta_corporativa_so_vale_com_orgao() -> None:
    assert criar_usuario(perfil=Perfil.CORPORATIVO, orgao=Orgao.EMLURB).e_corporativo
    assert not criar_usuario(perfil=Perfil.CORPORATIVO).e_corporativo
    assert not criar_usuario(perfil=Perfil.CORPORATIVO, orgao=Orgao.EMLURB).e_cidadao


def test_conta_excluida_e_reconhecida_pelo_email() -> None:
    usuario = criar_usuario()
    excluida = replace(usuario, email=email_da_conta_excluida(usuario.id))

    assert excluida.foi_excluido
    assert not usuario.foi_excluido


@pytest.mark.parametrize(
    ("alteracoes", "situacao"),
    [
        ({}, SituacaoDoAcesso.CONVITE_ENVIADO),
        ({"convite_expira_em": AGORA - timedelta(minutes=1)}, SituacaoDoAcesso.CONVITE_VENCIDO),
        ({"convite_aceito": True}, SituacaoDoAcesso.ATIVO),
        ({"convite_aceito": True, "ativo": False}, SituacaoDoAcesso.DESATIVADO),
    ],
)
def test_situacao_do_acesso(alteracoes: dict[str, object], situacao: SituacaoDoAcesso) -> None:
    assert acesso(**alteracoes).situacao(AGORA) is situacao


def test_convite_vale_uma_vez_e_so_ate_vencer() -> None:
    convite = ConviteDeAcesso(uuid4(), uuid4(), "hash", AGORA, AGORA + timedelta(days=7))

    assert convite.pode_ser_usado(AGORA)
    assert not convite.pode_ser_usado(AGORA + timedelta(days=7))
    assert not replace(convite, usado_em=AGORA).pode_ser_usado(AGORA)


def test_mesmo_local_tema_e_servico_na_mesma_semana_e_o_mesmo_problema() -> None:
    primeiro = ocorrencia_de_teste(1, **NO_MESMO_LOCAL)
    segundo = ocorrencia_de_teste(2, data_abertura=date(2026, 9, 4), **NO_MESMO_LOCAL)

    assert comparar_ocorrencias(primeiro, segundo).classe is ClasseDaComparacao.MESMA


def test_fontes_diferentes_nunca_sao_o_mesmo_problema() -> None:
    primeiro = ocorrencia_de_teste(1, **NO_MESMO_LOCAL)
    segundo = ocorrencia_de_teste(2, fonte=Fonte.FORMULARIO.value, **NO_MESMO_LOCAL)

    assert comparar_ocorrencias(primeiro, segundo).classe is ClasseDaComparacao.DISTINTA


def test_trinta_dias_ou_mais_deixa_de_ser_o_mesmo_problema() -> None:
    primeiro = ocorrencia_de_teste(1, **NO_MESMO_LOCAL)
    segundo = ocorrencia_de_teste(2, data_abertura=date(2026, 10, 1), **NO_MESMO_LOCAL)

    assert comparar_ocorrencias(primeiro, segundo).classe is ClasseDaComparacao.DISTINTA


def test_sem_pseudonimo_do_local_nao_ha_como_dizer_que_e_o_mesmo() -> None:
    sem_local = {"servico_codigo": "S1"}
    primeiro, segundo = ocorrencia_de_teste(1, **sem_local), ocorrencia_de_teste(2, **sem_local)

    assert comparar_ocorrencias(primeiro, segundo).classe is ClasseDaComparacao.DISTINTA


def test_busca_ignora_o_proprio_registro_e_ordena_pela_pontuacao() -> None:
    alvo = encaminhamento_de_teste(1, **NO_MESMO_LOCAL)
    candidatos = [
        alvo,
        encaminhamento_de_teste(2, data_abertura=date(2026, 9, 20), **NO_MESMO_LOCAL),
        encaminhamento_de_teste(3, **NO_MESMO_LOCAL),
    ]

    achados = encontrar_mesmo_problema(alvo.ocorrencia, candidatos)

    assert [item.encaminhamento.id for item in achados] == [3, 2]
    assert achados[0].e_certo


def test_grupos_se_formam_por_ligacao() -> None:
    encaminhamentos = [
        encaminhamento_de_teste(1, **NO_MESMO_LOCAL),
        encaminhamento_de_teste(2, data_abertura=date(2026, 9, 20), **NO_MESMO_LOCAL),
        encaminhamento_de_teste(3, data_abertura=date(2026, 10, 9), **NO_MESMO_LOCAL),
        encaminhamento_de_teste(4, bairro_oficial="BOA VIAGEM", **NO_MESMO_LOCAL),
    ]

    grupos = agrupar_mesmo_problema(encaminhamentos)

    assert [[item.id for item in grupo] for grupo in grupos] == [[1, 2, 3]]


def test_previsao_so_vale_no_atendimento_e_entre_hoje_e_um_ano() -> None:
    recebido = SituacaoDoEncaminhamento.RECEBIDO
    exigir_previsao_valida(recebido, HOJE, HOJE)
    exigir_previsao_valida(SituacaoDoEncaminhamento.RESOLVIDO, None, HOJE)
    with pytest.raises(EncaminhamentoInvalido):
        exigir_previsao_valida(recebido, HOJE - timedelta(days=1), HOJE)
    with pytest.raises(EncaminhamentoInvalido):
        exigir_previsao_valida(recebido, HOJE + timedelta(days=400), HOJE)
    with pytest.raises(EncaminhamentoInvalido):
        exigir_previsao_valida(SituacaoDoEncaminhamento.RESOLVIDO, HOJE, HOJE)


def test_previsao_some_depois_que_o_orgao_resolve() -> None:
    atendimento = EventoDoEncaminhamento(
        SituacaoDoEncaminhamento.RECEBIDO, AutorDoEvento.ORGAO, AGORA, previsao=date(2026, 12, 1)
    )
    recebido = replace(
        encaminhamento_de_teste(1, protocolo="TESTE-1"),
        situacao=SituacaoDoEncaminhamento.RECEBIDO,
        eventos=(atendimento,),
    )

    assert recebido.previsao == date(2026, 12, 1)
    assert replace(recebido, situacao=SituacaoDoEncaminhamento.RESOLVIDO).previsao is None


def test_aviso_ao_cidadao_leva_a_resposta_e_a_previsao_mas_nunca_a_nota_interna() -> None:
    evento = EventoDoEncaminhamento(
        SituacaoDoEncaminhamento.RECEBIDO,
        AutorDoEvento.ORGAO,
        AGORA,
        observacao="Equipe B, ordem 77",
        resposta_ao_cidadao="Vamos desobstruir a galeria",
        previsao=date(2026, 12, 1),
    )
    recebido = replace(
        encaminhamento_de_teste(1, protocolo="TESTE-1"),
        situacao=SituacaoDoEncaminhamento.RECEBIDO,
        eventos=(evento,),
    )

    aviso = aviso_ao_cidadao(recebido, ENDERECO_DO_SITE)

    assert "está em atendimento por Emlurb" in aviso.resumo
    assert "Resposta de Emlurb: Vamos desobstruir a galeria" in aviso.corpo
    assert "Previsão de conclusão: 01/12/2026" in aviso.corpo
    assert "Equipe B" not in aviso.corpo
    assert aviso.caminho == "/cidade/meus-pedidos"


def test_avisos_ao_orgao_apontam_para_a_area_corporativa() -> None:
    encaminhamento = encaminhamento_de_teste(7)

    nova = aviso_de_nova_ocorrencia(encaminhamento, ENDERECO_DO_SITE)
    vencido = aviso_de_prazo_vencido(encaminhamento, ENDERECO_DO_SITE)

    assert nova.caminho == vencido.caminho == "/corporativo/ocorrencias/7"
    assert "Drenagem em AFOGADOS" in nova.resumo
    assert "venceu em 19/12/2026" in vencido.resumo
    assert f"{ENDERECO_DO_SITE}/corporativo/ocorrencias/7" in nova.corpo


def test_a_defesa_civil_aparece_como_sedec_nas_fontes() -> None:
    assert "SEDEC" in nomes_na_fonte(Orgao.DEFESA_CIVIL)
    assert nomes_na_fonte(Orgao.COMPESA) == ["COMPESA"]


def test_percentual_no_prazo_so_existe_com_resolucao() -> None:
    assert IndicadoresDoOrgao(Orgao.CTTU).pct_no_prazo is None
    medido = IndicadoresDoOrgao(Orgao.CTTU, resolvidas=4, resolvidas_no_prazo=3)
    assert medido.pct_no_prazo == 75
