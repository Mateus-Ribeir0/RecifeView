from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencias import obter_servicos_de_encaminhamento
from app.api.dependencias_corporativas import (
    obter_comparacao_dos_orgaos,
    obter_notificacoes_da_conta,
    obter_servicos_de_acessos_corporativos,
    obter_servicos_do_orgao,
)
from app.application.casos_de_uso.acessos_corporativos.servicos import (
    ServicosDeAcessosCorporativos,
)
from app.application.casos_de_uso.encaminhamentos.desempenho import CompararOrgaos
from app.application.casos_de_uso.encaminhamentos.encaminhar import (
    EncaminharOcorrencia,
    PedidoDeEncaminhamento,
)
from app.application.casos_de_uso.notificacoes import NotificacoesDaConta
from app.application.sessoes import GestaoDeSessoes
from app.domain.email import Email
from app.domain.encaminhamento.orgaos import CATALOGO_DE_ORGAOS, Orgao
from app.domain.notificacao import NovaNotificacao
from app.domain.usuario import Perfil, Usuario
from tests.api.test_rotas_de_contas_e_perfis import BASE, Ambiente, token_de
from tests.fakes import HashDeSenhaDeTeste, criar_usuario
from tests.fakes_corporativo import (
    ENDERECO_DO_SITE,
    PADRAO_DO_CONVITE,
    AcessosCorporativosEmMemoria,
    ConvitesEmMemoria,
    IndicadoresEmMemoria,
    servicos_do_orgao,
)
from tests.fakes_encaminhamento import Ambiente as CicloEmMemoria
from tests.fakes_encaminhamento import EncaminhamentosEmMemoria, ocorrencia_de_teste

ROTAS_DO_ORGAO = [
    ("get", "/corporativo/painel"),
    ("get", "/corporativo/ocorrencias"),
    ("get", "/corporativo/ocorrencias/1"),
    ("post", "/corporativo/ocorrencias/1/resposta"),
    ("get", "/corporativo/dados"),
]
SENHA_FORTE = "Compesa@Recife2026"
RESOLVIDO = {"situacao": "resolvido", "resposta_ao_cidadao": "Vazamento consertado na rua"}


class AmbienteCorporativo(Ambiente):
    def __init__(self) -> None:
        super().__init__()
        self.administradora = criar_usuario(
            email=Email("administracao@recife.pe.gov.br"), perfil=Perfil.ADMINISTRADOR
        )
        self.compesa = criar_usuario(
            email=Email("equipe@compesa.exemplo"), perfil=Perfil.CORPORATIVO, orgao=Orgao.COMPESA
        )
        self.usuarios.adicionar(self.administradora)
        self.usuarios.adicionar(self.compesa)
        self.convites = ConvitesEmMemoria()
        self.ciclo = CicloEmMemoria(
            EncaminhamentosEmMemoria(ocorrencia_de_teste(7), ocorrencia_de_teste(8)),
            relogio=self.relogio,
        )
        self.ciclo.destinatarios.quem_acompanha = ["moradora@exemplo.com"]

    def servicos_de_acessos(self) -> ServicosDeAcessosCorporativos:
        return ServicosDeAcessosCorporativos(
            usuarios=self.usuarios,
            convites=self.convites,
            acessos=AcessosCorporativosEmMemoria(self.usuarios, self.convites),
            senhas=HashDeSenhaDeTeste(),
            emails=self.emails,
            registro=self.acessos,
            sessoes=GestaoDeSessoes(self.sessoes, self.emissor, self.relogio),
            relogio=self.relogio,
            endereco_do_site=ENDERECO_DO_SITE,
        )

    def encaminhar(self, chave: int, orgao: Orgao = Orgao.COMPESA) -> int:
        pedido = PedidoDeEncaminhamento(chave, orgao, uuid4())
        return EncaminharOcorrencia(self.ciclo.servicos()).executar(pedido).id

    def montar(self) -> FastAPI:
        app = super().montar()
        app.dependency_overrides[obter_servicos_de_acessos_corporativos] = self.servicos_de_acessos
        app.dependency_overrides[obter_servicos_de_encaminhamento] = self.ciclo.servicos
        app.dependency_overrides[obter_servicos_do_orgao] = lambda: servicos_do_orgao(self.ciclo)
        app.dependency_overrides[obter_notificacoes_da_conta] = lambda: NotificacoesDaConta(
            self.ciclo.notificacoes, self.relogio
        )
        app.dependency_overrides[obter_comparacao_dos_orgaos] = lambda: CompararOrgaos(
            self.ciclo.servicos(),
            IndicadoresEmMemoria(),
            AcessosCorporativosEmMemoria(self.usuarios, self.convites),
        )
        return app


@pytest.fixture
def ambiente() -> AmbienteCorporativo:
    return AmbienteCorporativo()


@pytest.fixture
def cliente(ambiente: AmbienteCorporativo) -> Iterator[TestClient]:
    with TestClient(ambiente.montar()) as testes:
        yield testes


def cabecalho(cliente: TestClient, usuario: Usuario, area: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_de(cliente, usuario, area)}"}


def test_conta_do_orgao_entra_pela_area_corporativa(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    cabecalhos = cabecalho(cliente, ambiente.compesa, "corporativo")

    eu = cliente.get(f"{BASE}/autenticacao/eu", headers=cabecalhos)

    assert eu.json()["orgao"] == "COMPESA"
    assert eu.json()["nome_do_orgao"] == "Compesa"


@pytest.mark.parametrize("perfil", ["cidadao", "gestora"])
def test_outros_perfis_nao_entram_pela_area_corporativa(
    cliente: TestClient, ambiente: AmbienteCorporativo, perfil: str
) -> None:
    usuario = ambiente.cidadao if perfil == "cidadao" else ambiente.gestora
    resposta = cliente.post(
        f"{BASE}/autenticacao/entrar",
        json={"email": str(usuario.email), "senha": "senha-correta-123", "area": "corporativo"},
    )

    assert resposta.status_code == 403
    assert resposta.json()["erro"]["codigo"] == "area_corporativa_negada"


@pytest.mark.parametrize(("metodo", "caminho"), ROTAS_DO_ORGAO)
def test_cidadao_e_gestao_recebem_403_na_area_corporativa(
    cliente: TestClient, ambiente: AmbienteCorporativo, metodo: str, caminho: str
) -> None:
    for usuario, area in ((ambiente.cidadao, "cidade"), (ambiente.gestora, "gestao")):
        resposta = cliente.request(
            metodo, f"{BASE}{caminho}", headers=cabecalho(cliente, usuario, area), json=RESOLVIDO
        )
        assert resposta.status_code == 403


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("get", "/encaminhamentos"),
        ("get", "/acessos-corporativos"),
        ("get", "/cidade/meus-relatos"),
        ("get", "/cidade/pedidos"),
    ],
)
def test_conta_do_orgao_nao_abre_a_gestao_nem_a_cidade(
    cliente: TestClient, ambiente: AmbienteCorporativo, metodo: str, caminho: str
) -> None:
    resposta = cliente.request(
        metodo, f"{BASE}{caminho}", headers=cabecalho(cliente, ambiente.compesa, "corporativo")
    )

    assert resposta.status_code == 403


def test_gestao_publica_ve_os_acessos_mas_nao_cria(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    cabecalhos = cabecalho(cliente, ambiente.gestora, "gestao")
    novo = {"nome": "Ana Souza", "email": "ana@compesa.exemplo", "orgao": "COMPESA"}

    lista = cliente.get(f"{BASE}/acessos-corporativos", headers=cabecalhos)
    criacao = cliente.post(f"{BASE}/acessos-corporativos", headers=cabecalhos, json=novo)

    assert lista.json()["pode_alterar"] is False
    assert [item["orgao"] for item in lista.json()["itens"]] == ["COMPESA"]
    assert criacao.status_code == 403
    assert criacao.json()["erro"]["codigo"] == "so_da_administracao"


def test_administracao_cria_o_acesso_e_a_pessoa_entra_pelo_convite(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    cabecalhos = cabecalho(cliente, ambiente.administradora, "gestao")
    novo = {"nome": "Ana Souza", "email": "ana@neoenergia.exemplo", "orgao": "NEOENERGIA"}

    criado = cliente.post(f"{BASE}/acessos-corporativos", headers=cabecalhos, json=novo)
    achado = PADRAO_DO_CONVITE.search(ambiente.emails.mensagens[-1].corpo)
    assert achado is not None
    token = achado.group(1)
    aberto = cliente.post(f"{BASE}/convites/abrir", json={"token": token})
    aceito = cliente.post(f"{BASE}/convites/aceitar", json={"token": token, "senha": SENHA_FORTE})

    assert criado.status_code == 201
    assert criado.json()["situacao"] == "convite_enviado"
    assert aberto.json()["nome_do_orgao"] == "Neoenergia Pernambuco"
    assert aceito.status_code == 200
    assert aceito.json()["usuario"]["perfil"] == "CORPORATIVO"
    repetido = cliente.post(f"{BASE}/convites/aceitar", json={"token": token, "senha": SENHA_FORTE})
    assert repetido.json()["erro"]["codigo"] == "convite_invalido"


def test_orgao_ve_a_fila_e_responde_ao_cidadao(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    identificador = ambiente.encaminhar(7)
    ambiente.encaminhar(8, Orgao.EMLURB)
    cabecalhos = cabecalho(cliente, ambiente.compesa, "corporativo")
    rota = f"{BASE}/corporativo/ocorrencias/{identificador}"

    fila = cliente.get(f"{BASE}/corporativo/ocorrencias", headers=cabecalhos)
    sem_explicacao = cliente.post(
        f"{rota}/resposta", headers=cabecalhos, json={"situacao": "resolvido"}
    )
    resposta = cliente.post(f"{rota}/resposta", headers=cabecalhos, json=RESOLVIDO)
    detalhe = cliente.get(rota, headers=cabecalhos)

    assert [item["id"] for item in fila.json()["itens"]] == [identificador]
    assert "protocolo_de_origem" not in fila.json()["itens"][0]
    assert sem_explicacao.status_code == 422
    assert resposta.json()["situacao"] == "resolvido"
    assert detalhe.json()["resposta_ao_cidadao"] == RESOLVIDO["resposta_ao_cidadao"]
    assert detalhe.json()["pode_responder"] is False


def test_ocorrencia_de_outro_orgao_responde_404(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    identificador = ambiente.encaminhar(8, Orgao.EMLURB)

    resposta = cliente.get(
        f"{BASE}/corporativo/ocorrencias/{identificador}",
        headers=cabecalho(cliente, ambiente.compesa, "corporativo"),
    )

    assert resposta.status_code == 404


def test_cada_conta_ve_e_marca_as_proprias_notificacoes(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    ambiente.ciclo.notificacoes.criar(
        NovaNotificacao(ambiente.cidadao.id, "Andamento: Compesa", "Foi resolvido.", "/cidade")
    )
    do_cidadao = cabecalho(cliente, ambiente.cidadao, "cidade")

    caixa = cliente.get(f"{BASE}/notificacoes", headers=do_cidadao)
    leitura = cliente.post(f"{BASE}/notificacoes/leitura", headers=do_cidadao)
    depois = cliente.get(f"{BASE}/notificacoes", headers=do_cidadao)
    da_gestora = cliente.get(
        f"{BASE}/notificacoes", headers=cabecalho(cliente, ambiente.gestora, "gestao")
    )

    assert caixa.json()["nao_lidas"] == 1
    assert caixa.json()["itens"][0]["caminho"] == "/cidade"
    assert leitura.status_code == 204
    assert depois.json()["nao_lidas"] == 0
    assert da_gestora.json()["itens"] == []


def test_notificacoes_exigem_conta(cliente: TestClient) -> None:
    assert cliente.get(f"{BASE}/notificacoes").status_code == 401


def test_gestao_compara_todos_os_orgaos_do_catalogo(
    cliente: TestClient, ambiente: AmbienteCorporativo
) -> None:
    resposta = cliente.get(
        f"{BASE}/encaminhamentos/desempenho", headers=cabecalho(cliente, ambiente.gestora, "gestao")
    )

    orgaos = {item["orgao"]: item for item in resposta.json()["orgaos"]}
    assert set(orgaos) == {dados.orgao.value for dados in CATALOGO_DE_ORGAOS}
    assert orgaos["COMPESA"]["acessos_ativos"] == 1
