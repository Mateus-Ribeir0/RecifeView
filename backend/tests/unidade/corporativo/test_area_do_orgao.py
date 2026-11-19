from datetime import timedelta
from uuid import uuid4

import pytest

from app.application.casos_de_uso.corporativo.ocorrencias import (
    AbaDoOrgao,
    ConsultarOcorrenciaDoOrgao,
    ListarOcorrenciasDoOrgao,
    PedidoDaFila,
)
from app.application.casos_de_uso.corporativo.painel import (
    ConsultarDemandaDoOrgao,
    MontarPainelDoOrgao,
)
from app.application.casos_de_uso.corporativo.resposta import ResponderComoOrgao, RespostaDoOrgao
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
    PrepararEncaminhamento,
)
from app.application.casos_de_uso.encaminhamentos.lembrete import LembrarOrgaos
from app.application.casos_de_uso.encaminhamentos.retorno import RespostaAoEncaminhamento
from app.domain.demanda_do_orgao import PeriodoEmAnos
from app.domain.encaminhamento.desempenho import IndicadoresDoOrgao
from app.domain.encaminhamento.encaminhamento import (
    DIAS_PARA_O_ORGAO_RESPONDER,
    AutorDoEvento,
    CanalDeEnvio,
    Encaminhamento,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.erros import AcessoNegado, EncaminhamentoInvalido, EncaminhamentoNaoEncontrado
from app.domain.usuario import Perfil
from tests.fakes import criar_usuario
from tests.fakes_corporativo import (
    DemandaEmMemoria,
    IndicadoresEmMemoria,
    criar_conta_do_orgao,
    servicos_do_orgao,
)
from tests.fakes_encaminhamento import Ambiente, EncaminhamentosEmMemoria, ocorrencia_de_teste

COMPESA = criar_conta_do_orgao(Orgao.COMPESA)
GESTORA = "gestora@exemplo.gov.br"
MORADORA = "moradora@exemplo.com"
PESSOA_DA_COMPESA = "equipe@compesa.exemplo"
NO_MESMO_LOCAL = {"id_local": "local-1", "numero_informado": True, "servico_codigo": "S1"}
RESOLVIDO = RespostaAoEncaminhamento(
    SituacaoDoEncaminhamento.RESOLVIDO,
    observacao="Ordem de serviço 4411",
    resposta_ao_cidadao="A galeria foi desobstruída",
)


def ambiente_com(*chaves: int, **ocorrencia: object) -> Ambiente:
    repositorio = EncaminhamentosEmMemoria(
        *(ocorrencia_de_teste(chave, protocolo=f"TESTE-{chave}", **ocorrencia) for chave in chaves)
    )
    ambiente = Ambiente(repositorio)
    ambiente.destinatarios.quem_encaminhou = GESTORA
    ambiente.destinatarios.quem_acompanha = [MORADORA]
    return ambiente


def encaminhar(ambiente: Ambiente, chave: int, orgao: Orgao = Orgao.COMPESA) -> int:
    pedido = PedidoDeEncaminhamento(chave, orgao, uuid4())
    return EncaminharOcorrencia(ambiente.servicos()).executar(pedido).id


def responder(ambiente: Ambiente, pedido: RespostaDoOrgao) -> None:
    ResponderComoOrgao(servicos_do_orgao(ambiente)).executar(COMPESA, pedido)


def guardado(ambiente: Ambiente, identificador: int) -> Encaminhamento:
    encaminhamento = ambiente.repositorio.buscar(identificador)
    assert encaminhamento is not None
    return encaminhamento


def test_fila_mostra_so_o_que_foi_para_o_orgao() -> None:
    ambiente = ambiente_com(1, 2)
    encaminhar(ambiente, 1)
    encaminhar(ambiente, 2, Orgao.EMLURB)

    fila = ListarOcorrenciasDoOrgao(servicos_do_orgao(ambiente)).executar(
        Orgao.COMPESA, PedidoDaFila(AbaDoOrgao.NOVAS)
    )

    assert [item.encaminhamento.orgao for item in fila.itens] == [Orgao.COMPESA]
    assert fila.itens[0].pessoas_que_acompanham == 1


def test_fila_conta_o_mesmo_problema_dentro_e_fora_do_orgao() -> None:
    ambiente = ambiente_com(1, 2, 3, **NO_MESMO_LOCAL)
    for chave, orgao in ((1, Orgao.COMPESA), (2, Orgao.COMPESA), (3, Orgao.EMLURB)):
        encaminhar(ambiente, chave, orgao)

    fila = ListarOcorrenciasDoOrgao(servicos_do_orgao(ambiente)).executar(
        Orgao.COMPESA, PedidoDaFila(AbaDoOrgao.NOVAS)
    )

    contagens = {
        (item.mesmo_problema_no_orgao, item.mesmo_problema_em_outros_orgaos) for item in fila.itens
    }
    assert contagens == {(1, 1)}


def test_contagem_das_abas_vem_dos_indicadores_do_orgao() -> None:
    ambiente = ambiente_com(1)
    indicadores = IndicadoresEmMemoria([IndicadoresDoOrgao(Orgao.COMPESA, novas=4, vencidas=1)])

    fila = ListarOcorrenciasDoOrgao(servicos_do_orgao(ambiente, indicadores)).executar(
        Orgao.COMPESA, PedidoDaFila()
    )

    assert (fila.por_aba[AbaDoOrgao.NOVAS], fila.por_aba[AbaDoOrgao.VENCIDAS]) == (4, 1)


def test_outro_orgao_recebe_nao_encontrado_e_nao_sabe_que_existe() -> None:
    ambiente = ambiente_com(1)
    identificador = encaminhar(ambiente, 1, Orgao.EMLURB)

    with pytest.raises(EncaminhamentoNaoEncontrado):
        ConsultarOcorrenciaDoOrgao(servicos_do_orgao(ambiente)).executar(
            Orgao.COMPESA, identificador
        )


def test_conta_sem_orgao_nao_responde() -> None:
    ambiente = ambiente_com(1)
    identificador = encaminhar(ambiente, 1)

    with pytest.raises(AcessoNegado):
        ResponderComoOrgao(servicos_do_orgao(ambiente)).executar(
            criar_usuario(perfil=Perfil.GESTOR), RespostaDoOrgao(identificador, RESOLVIDO)
        )


def test_resolver_exige_contar_ao_cidadao_o_que_foi_feito() -> None:
    ambiente = ambiente_com(1)
    identificador = encaminhar(ambiente, 1)
    sem_resposta = RespostaAoEncaminhamento(SituacaoDoEncaminhamento.RESOLVIDO)

    with pytest.raises(EncaminhamentoInvalido) as erro:
        responder(ambiente, RespostaDoOrgao(identificador, sem_resposta))
    assert erro.value.campo == "resposta_ao_cidadao"


def test_resolucao_avisa_o_cidadao_com_a_resposta_e_a_gestao_no_sino() -> None:
    ambiente = ambiente_com(1)
    identificador = encaminhar(ambiente, 1)

    responder(ambiente, RespostaDoOrgao(identificador, RESOLVIDO))

    ultimo = ambiente.entrega.para(MORADORA)[-1]
    assert "A galeria foi desobstruída" in ultimo.corpo
    assert "Ordem de serviço" not in ultimo.corpo
    (no_sino_da_gestao,) = ambiente.notificacoes.para(GESTORA)
    assert no_sino_da_gestao.caminho == f"/painel/encaminhamentos/{identificador}"
    evento = guardado(ambiente, identificador).eventos[-1]
    assert evento.autor is AutorDoEvento.ORGAO
    assert evento.resposta_ao_cidadao == "A galeria foi desobstruída"


def test_atendimento_com_previsao_pode_ser_atualizado() -> None:
    ambiente = ambiente_com(1)
    identificador = encaminhar(ambiente, 1)
    hoje = ambiente.relogio.agora().date()
    for dias in (10, 15):
        atendimento = RespostaAoEncaminhamento(
            SituacaoDoEncaminhamento.RECEBIDO, previsao=hoje + timedelta(days=dias)
        )
        responder(ambiente, RespostaDoOrgao(identificador, atendimento))

    assert guardado(ambiente, identificador).previsao == hoje + timedelta(days=15)
    assert "Previsão de conclusão" in ambiente.entrega.para(MORADORA)[-1].corpo


def test_resposta_vale_para_todas_as_ocorrencias_do_mesmo_problema() -> None:
    ambiente = ambiente_com(1, 2, **NO_MESMO_LOCAL)
    primeiro, segundo = encaminhar(ambiente, 1), encaminhar(ambiente, 2)

    responder(ambiente, RespostaDoOrgao(primeiro, RESOLVIDO, (segundo,)))

    situacoes = {guardado(ambiente, item).situacao for item in (primeiro, segundo)}
    assert situacoes == {SituacaoDoEncaminhamento.RESOLVIDO}


def test_resposta_em_grupo_recusa_outro_problema_sem_gravar_nada() -> None:
    ambiente = ambiente_com(1)
    ambiente.repositorio.ocorrencias[2] = ocorrencia_de_teste(2, bairro_oficial="BOA VIAGEM")
    primeiro, segundo = encaminhar(ambiente, 1), encaminhar(ambiente, 2)

    with pytest.raises(EncaminhamentoInvalido):
        responder(ambiente, RespostaDoOrgao(primeiro, RESOLVIDO, (segundo,)))
    assert guardado(ambiente, primeiro).situacao is SituacaoDoEncaminhamento.ENVIADO


def test_orgao_com_acesso_recebe_pela_plataforma_e_no_sino() -> None:
    ambiente = ambiente_com(1)
    ambiente.destinatarios.do_orgao[Orgao.COMPESA] = [PESSOA_DA_COMPESA]

    canais = PrepararEncaminhamento(ambiente.servicos()).executar(1).canais
    identificador = encaminhar(ambiente, 1)

    assert canais[Orgao.COMPESA] is CanalDeEnvio.PLATAFORMA
    assert canais[Orgao.EMLURB] is CanalDeEnvio.LOCAL
    assert ambiente.despacho.enviadas == []
    (aviso,) = ambiente.notificacoes.para(PESSOA_DA_COMPESA)
    assert aviso.caminho == f"/corporativo/ocorrencias/{identificador}"
    assert len(ambiente.entrega.para(PESSOA_DA_COMPESA)) == 1


def test_prazo_vencido_vai_para_o_sino_do_orgao_sem_mensagem_externa() -> None:
    ambiente = ambiente_com(1)
    ambiente.destinatarios.do_orgao[Orgao.COMPESA] = [PESSOA_DA_COMPESA]
    encaminhar(ambiente, 1)
    ambiente.relogio.avancar(timedelta(days=DIAS_PARA_O_ORGAO_RESPONDER + 1))

    resultado = LembrarOrgaos(ambiente.servicos()).executar()

    assert resultado.enviados == 1
    assert ambiente.despacho.enviadas == []
    assert ambiente.notificacoes.para(PESSOA_DA_COMPESA)[-1].titulo.startswith("Prazo vencido")


def test_painel_junta_o_mesmo_problema_e_mostra_o_mais_urgente_primeiro() -> None:
    ambiente = ambiente_com(1, 2, **NO_MESMO_LOCAL)
    encaminhar(ambiente, 1)
    ambiente.relogio.avancar(timedelta(days=2))
    encaminhar(ambiente, 2)

    painel = MontarPainelDoOrgao(servicos_do_orgao(ambiente)).executar(Orgao.COMPESA)

    assert [item.ocorrencia.chave_registro for item in painel.mais_urgentes] == [1, 2]
    assert len(painel.grupos_do_mesmo_problema) == 1


def test_dados_do_orgao_buscam_os_nomes_que_a_fonte_usa() -> None:
    servicos = servicos_do_orgao(ambiente_com(1))
    periodo = PeriodoEmAnos(2021, 2025)

    ConsultarDemandaDoOrgao(servicos).executar(Orgao.DEFESA_CIVIL, periodo)

    assert isinstance(servicos.demanda, DemandaEmMemoria)
    (nomes, recebido), *_ = servicos.demanda.pedidos
    assert "SEDEC" in nomes
    assert recebido == periodo
