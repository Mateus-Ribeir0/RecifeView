from collections.abc import Generator, Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencias import abrir_transacao
from app.application.casos_de_uso.contas.criar_conta import CriarConta, NovaConta
from app.application.casos_de_uso.contas.recuperar_senha import PedirNovaSenha
from app.application.casos_de_uso.contas.servicos import ServicosDeConta
from app.application.portas.contas import EnvioDeEmailFalhou, MensagemDeEmail
from app.application.portas.contribuicoes import FiltroDaCidade
from app.application.sessoes import GestaoDeSessoes
from app.domain.email import Email
from app.infrastructure.auth.senhas import HashDeSenhaArgon2
from app.infrastructure.auth.tokens import EmissorDeTokenJwt
from app.infrastructure.email.caixa_de_saida_local import CaixaDeSaidaLocal
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.repositories.acessos import RegistroDeAcessosSql
from app.infrastructure.repositories.codigos_de_conta import CodigoDeContaRepositorySql
from app.infrastructure.repositories.contribuicoes import ContribuicaoRepositorySql
from app.infrastructure.repositories.sessoes import SessaoRepositorySql
from app.infrastructure.repositories.usuarios import UsuarioRepositorySql
from tests.conftest import SEGREDO_DE_TESTE
from tests.integracao.test_importacao_e_painel import URL_DO_BANCO_DE_TESTE, preparar_esquema

pytestmark = pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)

SENHA = "uma senha bem comprida"


@pytest.fixture
def fabrica(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    assert URL_DO_BANCO_DE_TESTE
    preparar_esquema(URL_DO_BANCO_DE_TESTE, monkeypatch)
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    yield sessionmaker(motor, expire_on_commit=False)
    motor.dispose()


def servicos(sessao: Session, pasta: Path) -> ServicosDeConta:
    relogio = RelogioDoSistema()
    emissor = EmissorDeTokenJwt(SEGREDO_DE_TESTE, timedelta(minutes=15))
    return ServicosDeConta(
        usuarios=UsuarioRepositorySql(sessao),
        codigos=CodigoDeContaRepositorySql(sessao),
        senhas=HashDeSenhaArgon2(),
        emails=CaixaDeSaidaLocal(pasta),
        acessos=RegistroDeAcessosSql(sessao),
        sessoes=GestaoDeSessoes(SessaoRepositorySql(sessao), emissor, relogio),
        relogio=relogio,
    )


def codigo_do_email(pasta: Path) -> str:
    (arquivo,) = sorted(pasta.iterdir())
    linha = next(item for item in arquivo.read_text().splitlines() if item[:3].isdigit())
    return linha.replace(" ", "")


def criar_conta(fabrica: sessionmaker[Session], pasta: Path) -> None:
    nova = NovaConta("Maria da Silva", "maria@exemplo.com", SENHA, "AFOGADOS", True)
    with fabrica.begin() as sessao:
        CriarConta(servicos(sessao, pasta), frozenset({"AFOGADOS"})).executar(nova)


def test_cadastro_grava_a_conta_pronta_para_entrar(
    fabrica: sessionmaker[Session], tmp_path: Path
) -> None:
    criar_conta(fabrica, tmp_path)

    with fabrica() as sessao:
        usuario = UsuarioRepositorySql(sessao).buscar_por_email(Email("maria@exemplo.com"))
        sessoes = sessao.scalar(text("SELECT count(*) FROM app.sessao"))
    assert usuario is not None
    assert usuario.bairro_oficial == "AFOGADOS"
    assert sessoes == 1
    assert list(tmp_path.iterdir()) == []


def test_codigo_de_nova_senha_vai_para_fora_do_git_e_so_o_hash_fica_no_banco(
    fabrica: sessionmaker[Session], tmp_path: Path
) -> None:
    criar_conta(fabrica, tmp_path)
    with fabrica.begin() as sessao:
        PedirNovaSenha(servicos(sessao, tmp_path)).executar("maria@exemplo.com")

    codigo = codigo_do_email(tmp_path)
    with fabrica() as sessao:
        guardado = sessao.scalar(text("SELECT hash_do_codigo FROM app.codigo_de_conta"))
    assert codigo not in str(guardado)
    assert SENHA not in next(tmp_path.iterdir()).read_text()


class EnvioForaDoAr:
    def enviar(self, mensagem: MensagemDeEmail) -> None:
        raise EnvioDeEmailFalhou


def test_falha_no_envio_desfaz_o_codigo(fabrica: sessionmaker[Session], tmp_path: Path) -> None:
    criar_conta(fabrica, tmp_path)
    pedido = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(fabrica_de_sessoes=fabrica)))
    transacao = cast(Generator[Session], abrir_transacao(pedido))  # type: ignore[arg-type]
    sem_envio = replace(servicos(next(transacao), tmp_path), emails=EnvioForaDoAr())

    with pytest.raises(EnvioDeEmailFalhou) as falha:
        PedirNovaSenha(sem_envio).executar("maria@exemplo.com")
    with pytest.raises(EnvioDeEmailFalhou):
        transacao.throw(falha.value)

    with fabrica() as sessao:
        codigos = sessao.scalar(text("SELECT count(*) FROM app.codigo_de_conta"))
    assert codigos == 0


def inserir_relato(sessao: Session, logradouro: str, numero: str) -> None:
    sessao.execute(
        text(
            "INSERT INTO app.contribuicao (id, chave_de_envio, recebida_em, data_relato, "
            "categoria, servico_codigo, servico, bairro_oficial, logradouro, numero, detalhe, "
            "numero_informado, retorno, resultado) VALUES (:id, :chave, :agora, :hoje, "
            "'PAVIMENTACAO', '131', 'OPERACAO TAPA-BURACO', 'AFOGADOS', :logradouro, :numero, "
            "'texto que o cidadão não pode ver', true, 'registrou_sem_retorno', 'nova')"
        ),
        {
            "id": uuid4(),
            "chave": uuid4().hex,
            "agora": datetime.now(UTC),
            "hoje": datetime.now(UTC).date(),
            "logradouro": logradouro,
            "numero": numero,
        },
    )


def test_visao_da_cidade_so_mostra_rua_da_lista_oficial(fabrica: sessionmaker[Session]) -> None:
    with fabrica.begin() as sessao:
        sessao.execute(
            text("INSERT INTO ouro.dim_logradouro VALUES ('AFOGADOS', 'RUA DA ESPERANCA', 10)")
        )
        inserir_relato(sessao, "RUA DA ESPERANCA", "128")
        inserir_relato(sessao, "RUA INVENTADA PARA OFENDER", "5")

    repositorio = ContribuicaoRepositorySql(fabrica)
    hoje = datetime.now(UTC).date()
    linhas = repositorio.ocorrencias_da_cidade(FiltroDaCidade(hoje - timedelta(days=90)))

    vias = sorted(str(item.via_reconhecida) for item in linhas)
    assert vias == ["None", "RUA DA ESPERANCA"]
    assert all(item.sem_retorno == 1 for item in linhas)
    filtradas = repositorio.ocorrencias_da_cidade(
        FiltroDaCidade(hoje - timedelta(days=90), "IPUTINGA")
    )
    assert filtradas == []
    por_tema = repositorio.ocorrencias_da_cidade(
        FiltroDaCidade(hoje - timedelta(days=90), None, ("ILUMINACAO PUBLICA",))
    )
    assert por_tema == []


def inserir_relato_de(
    sessao: Session, usuario_id: UUID | None, principal_id: UUID | None = None
) -> UUID:
    identificador = uuid4()
    sessao.execute(
        text(
            "INSERT INTO app.contribuicao (id, chave_de_envio, recebida_em, data_relato, "
            "categoria, servico_codigo, servico, bairro_oficial, logradouro, numero, "
            "numero_informado, retorno, resultado, principal_id, usuario_id) VALUES (:id, "
            ":chave, :agora, :hoje, 'PAVIMENTACAO', '131', 'OPERACAO TAPA-BURACO', 'AFOGADOS', "
            "'RUA DA ESPERANCA', '128', true, 'nao_registrou', :resultado, :principal, :usuario)"
        ),
        {
            "id": identificador,
            "chave": uuid4().hex,
            "agora": datetime.now(UTC),
            "hoje": datetime.now(UTC).date(),
            "resultado": "somada" if principal_id else "nova",
            "principal": principal_id,
            "usuario": usuario_id,
        },
    )
    return identificador


def test_meus_relatos_trazem_so_os_da_conta_e_a_situacao_da_ocorrencia(
    fabrica: sessionmaker[Session], tmp_path: Path
) -> None:
    criar_conta(fabrica, tmp_path)
    with fabrica() as sessao:
        maria = UsuarioRepositorySql(sessao).buscar_por_email(Email("maria@exemplo.com"))
    assert maria is not None
    with fabrica.begin() as sessao:
        sozinho = inserir_relato_de(sessao, maria.id)
        de_outra_pessoa = inserir_relato_de(sessao, None)
        somado = inserir_relato_de(sessao, maria.id, de_outra_pessoa)

    relatos = ContribuicaoRepositorySql(fabrica).relatos_do_cidadao(maria.id)

    por_id = {relato.id: relato for relato in relatos}
    assert set(por_id) == {sozinho, somado}
    assert (por_id[somado].somado, por_id[somado].relatos) == (True, 2)
    assert (por_id[sozinho].somado, por_id[sozinho].relatos) == (False, 1)
    assert {relato.situacao for relato in relatos} == {"aberta"}
    assert por_id[sozinho].logradouro == "RUA DA ESPERANCA"
