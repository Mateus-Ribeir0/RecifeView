from datetime import date, datetime, timedelta
from typing import cast
from uuid import uuid4

from app.application.casos_de_uso.cidade.meu_bairro import ConsultarMeuBairro
from app.application.casos_de_uso.cidade.meus_relatos import ListarMeusRelatos
from app.application.casos_de_uso.cidade.ocorrencias import ListarOcorrenciasDaCidade
from app.application.portas.contribuicoes import OcorrenciaDaCidade, RelatoDoCidadao
from app.domain.catalogos import BairroDoCatalogo
from app.domain.cidade import DIAS_DA_VISAO_DO_CIDADAO, SituacaoPublica
from app.domain.filtros import Filtros
from app.domain.territorio import VolumeDoBairro
from app.domain.usuario import Perfil
from app.domain.visao_geral import PercentisDePrazo
from tests.fakes import INICIO_DOS_TESTES, RelogioFixo, criar_usuario
from tests.fakes_importacao import ContribuicoesEmMemoria


def linha(via: str | None, numero: str | None) -> OcorrenciaDaCidade:
    return OcorrenciaDaCidade(
        id=uuid4(),
        data_relato=date(2026, 10, 20),
        servico_codigo="131",
        servico="OPERACAO TAPA-BURACO",
        bairro_oficial="AFOGADOS",
        bairro="Afogados",
        rpa="5",
        via_reconhecida=via,
        numero=numero,
        relatos=3,
        sem_retorno=2,
        situacao="aberta",
        tem_dupla_aberta=False,
    )


def listar(*linhas: OcorrenciaDaCidade, tema: str | None = None) -> list[object]:
    contribuicoes = ContribuicoesEmMemoria(da_cidade=list(linhas))
    caso = ListarOcorrenciasDaCidade(contribuicoes, RelogioFixo())
    return cast(list[object], caso.executar("AFOGADOS", tema))


def test_cidadao_ve_o_servico_em_linguagem_simples_e_a_centena() -> None:
    (ocorrencia,) = listar(linha("RUA DA ESPERANCA", "128"))

    assert ocorrencia.servico == "Buraco na rua"  # type: ignore[attr-defined]
    assert ocorrencia.tema == "Ruas e calçadas"  # type: ignore[attr-defined]
    assert ocorrencia.faixa_de_numeracao == "entre 100 e 199"  # type: ignore[attr-defined]
    assert ocorrencia.situacao is SituacaoPublica.RECEBIDO  # type: ignore[attr-defined]


def test_rua_fora_da_lista_oficial_nao_mostra_nem_a_faixa() -> None:
    (ocorrencia,) = listar(linha(None, "128"))

    assert ocorrencia.via is None  # type: ignore[attr-defined]
    assert ocorrencia.faixa_de_numeracao is None  # type: ignore[attr-defined]


def test_resposta_nao_tem_campo_para_numero_exato_nem_detalhe() -> None:
    (ocorrencia,) = listar(linha("RUA DA ESPERANCA", "128"))

    campos = set(vars(ocorrencia))
    assert not campos & {"numero", "detalhe", "logradouro", "id_local"}


def test_mostra_so_os_ultimos_90_dias_e_filtra_pelo_tema() -> None:
    contribuicoes = ContribuicoesEmMemoria()
    ListarOcorrenciasDaCidade(contribuicoes, RelogioFixo()).executar("AFOGADOS", "ruas")

    (filtro,) = contribuicoes.filtros_da_cidade
    assert filtro.desde == INICIO_DOS_TESTES.date() - timedelta(days=DIAS_DA_VISAO_DO_CIDADAO)
    assert filtro.categorias == ("ESCADARIA", "MANUT. URBANA", "PAVIMENTACAO")


class IndicadoresFalsos:
    def percentis_de_prazo(self, filtros: Filtros) -> PercentisDePrazo:
        return PercentisDePrazo(5, 60) if filtros.bairros else PercentisDePrazo(4, 55)

    def pct_local_repetido(self, filtros: Filtros) -> float | None:
        return 40.0 if filtros.bairros else 53.3


class TerritorioFalso:
    def volumes_de_156(self, filtros: Filtros) -> tuple[list[VolumeDoBairro], int]:
        return [VolumeDoBairro("AFOGADOS", 5000), VolumeDoBairro("RECIFE", 400)], 5

    def bairros(self) -> list[BairroDoCatalogo]:
        return [
            BairroDoCatalogo("AFOGADOS", "Afogados", "5", 10000, 28.9, taxa_confiavel=True),
            BairroDoCatalogo("RECIFE", "Recife", "1", 541, 0.0, taxa_confiavel=False),
        ]


def test_meu_bairro_compara_com_o_recife() -> None:
    caso = ConsultarMeuBairro(IndicadoresFalsos(), TerritorioFalso())  # type: ignore[arg-type]

    resultado = caso.executar("AFOGADOS")

    assert resultado.pedidos_ao_156 == 5000
    assert resultado.pedidos_por_mil_habitantes.bairro == 100.0
    assert resultado.prazo_p90.bairro == 60
    assert resultado.prazo_p90.recife == 55
    assert resultado.pct_local_repetido.recife == 53.3


def test_bairro_pequeno_nao_tem_taxa() -> None:
    caso = ConsultarMeuBairro(IndicadoresFalsos(), TerritorioFalso())  # type: ignore[arg-type]

    assert caso.executar("RECIFE").pedidos_por_mil_habitantes.bairro is None


def relato_meu(**mudancas: object) -> RelatoDoCidadao:
    dados: dict[str, object] = {
        "id": uuid4(),
        "recebida_em": datetime(2026, 10, 20, 9, 30),
        "servico_codigo": "131",
        "servico": "OPERACAO TAPA-BURACO",
        "bairro": "Afogados",
        "logradouro": "RUA DA ESPERANCA",
        "numero": "128",
        "detalhe": "Em frente à padaria",
        "endereco_apagado": False,
        "somado": False,
        "relatos": 1,
        "situacao": "aberta",
        "tem_dupla_aberta": False,
    }
    return RelatoDoCidadao(**(dados | mudancas))  # type: ignore[arg-type]


def test_meus_relatos_mostram_o_endereco_inteiro_e_a_situacao() -> None:
    cidadao = criar_usuario(perfil=Perfil.CIDADAO)
    em_analise = relato_meu(tem_dupla_aberta=True)
    no_painel = relato_meu(situacao="na_base", somado=True, relatos=4)
    contribuicoes = ContribuicoesEmMemoria(do_cidadao={cidadao.id: [em_analise, no_painel]})

    primeiro, segundo = ListarMeusRelatos(contribuicoes).executar(cidadao)

    assert primeiro.endereco == "RUA DA ESPERANCA, 128"
    assert primeiro.servico == "Buraco na rua"
    assert primeiro.situacao is SituacaoPublica.EM_ANALISE
    assert segundo.situacao is SituacaoPublica.NO_PAINEL
    assert (segundo.somado, segundo.relatos) == (True, 4)


def test_relato_com_endereco_apagado_fica_sem_endereco() -> None:
    cidadao = criar_usuario(perfil=Perfil.CIDADAO)
    apagado = relato_meu(logradouro=None, numero=None, detalhe=None, endereco_apagado=True)
    contribuicoes = ContribuicoesEmMemoria(do_cidadao={cidadao.id: [apagado]})

    (relato,) = ListarMeusRelatos(contribuicoes).executar(cidadao)

    assert relato.endereco is None
    assert relato.endereco_apagado


def test_quem_nao_relatou_nao_ve_relato_de_ninguem() -> None:
    dona = criar_usuario(perfil=Perfil.CIDADAO)
    outra = criar_usuario(perfil=Perfil.CIDADAO)
    contribuicoes = ContribuicoesEmMemoria(do_cidadao={dona.id: [relato_meu()]})

    assert ListarMeusRelatos(contribuicoes).executar(outra) == []
