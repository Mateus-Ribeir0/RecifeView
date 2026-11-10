from collections.abc import Generator, Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencias import abrir_transacao
from app.application.casos_de_uso.contas.confirmar_email import (
    ConfirmacaoDeEmail,
    ConfirmarEmail,
)
from app.application.casos_de_uso.contas.criar_conta import CriarConta, NovaConta
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


def test_cadastro_grava_o_email_fora_do_git_e_confirma(
    fabrica: sessionmaker[Session], tmp_path: Path
) -> None:
    nova = NovaConta("Maria da Silva", "maria@exemplo.com", SENHA, "AFOGADOS", True)
    with fabrica.begin() as sessao:
        CriarConta(servicos(sessao, tmp_path), frozenset({"AFOGADOS"})).executar(nova)

    codigo = codigo_do_email(tmp_path)
    assert SENHA not in next(tmp_path.iterdir()).read_text()
    with fabrica.begin() as sessao:
        confirmacao = ConfirmacaoDeEmail("maria@exemplo.com", codigo, SENHA)
        ConfirmarEmail(servicos(sessao, tmp_path)).executar(confirmacao)

    with fabrica() as sessao:
        usuario = UsuarioRepositorySql(sessao).buscar_por_email(Email("maria@exemplo.com"))
        guardado = sessao.scalar(text("SELECT hash_do_codigo FROM app.codigo_de_conta"))
    assert usuario is not None
    assert usuario.email_confirmado_em is not None
    assert usuario.bairro_oficial == "AFOGADOS"
    assert codigo not in str(guardado)


class EnvioForaDoAr:
    def enviar(self, mensagem: MensagemDeEmail) -> None:
        raise EnvioDeEmailFalhou


def test_falha_no_envio_desfaz_a_conta_e_o_codigo(
    fabrica: sessionmaker[Session], tmp_path: Path
) -> None:
    nova = NovaConta("Maria da Silva", "maria@exemplo.com", SENHA, "AFOGADOS", True)
    pedido = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(fabrica_de_sessoes=fabrica)))
    transacao = cast(Generator[Session], abrir_transacao(pedido))  # type: ignore[arg-type]
    sem_envio = replace(servicos(next(transacao), tmp_path), emails=EnvioForaDoAr())

    with pytest.raises(EnvioDeEmailFalhou) as falha:
        CriarConta(sem_envio, frozenset({"AFOGADOS"})).executar(nova)
    with pytest.raises(EnvioDeEmailFalhou):
        transacao.throw(falha.value)

    with fabrica() as sessao:
        usuario = UsuarioRepositorySql(sessao).buscar_por_email(Email("maria@exemplo.com"))
        codigos = sessao.scalar(text("SELECT count(*) FROM app.codigo_de_conta"))
    assert usuario is None
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
