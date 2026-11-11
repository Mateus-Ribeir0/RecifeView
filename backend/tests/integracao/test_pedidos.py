from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.repositories.pedidos import (
    ConsultaDePedidosSql,
    PedidoAcompanhadoRepositorySql,
)
from tests.integracao.test_importacao_e_painel import URL_DO_BANCO_DE_TESTE, preparar_esquema

pytestmark = pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)

AGORA = datetime(2026, 11, 11, 12, tzinfo=UTC)


@pytest.fixture
def fabrica(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    assert URL_DO_BANCO_DE_TESTE
    preparar_esquema(URL_DO_BANCO_DE_TESTE, monkeypatch)
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    yield sessionmaker(motor, expire_on_commit=False)
    motor.dispose()


def test_consulta_pelo_protocolo_devolve_so_o_registro_exato(
    fabrica: sessionmaker[Session],
) -> None:
    with fabrica.begin() as sessao:
        importacao = sessao.execute(
            text(
                "INSERT INTO app.importacao (nome_do_arquivo, tamanho_em_bytes, hash_do_arquivo, "
                "status, criada_em) VALUES ('t.csv', 1, 'x', 'CONCLUIDA', now()) RETURNING id"
            )
        ).scalar_one()
        for chave, protocolo in ((1, "2026/1"), (2, "2026/10"), (3, None)):
            sessao.execute(
                text(
                    "INSERT INTO ouro.fato_demanda (chave_registro, assinatura, importacao_id, "
                    "fonte, situacao, protocolo) VALUES (:chave, :chave, :importacao, "
                    "'OUVIDORIA', 'ABERTA', :protocolo)"
                ),
                {"chave": chave, "importacao": importacao, "protocolo": protocolo},
            )

    with fabrica() as sessao:
        registros = ConsultaDePedidosSql(sessao).registros("2026/1")

    assert [registro.chave_registro for registro in registros] == [1]
    assert registros[0].situacao == "ABERTA"


def test_pedidos_guardados_ficam_por_conta_e_saem_todos_juntos(
    fabrica: sessionmaker[Session],
) -> None:
    dona = uuid4()
    with fabrica.begin() as sessao:
        sessao.execute(
            text(
                "INSERT INTO app.usuario (id, email, nome, perfil, hash_da_senha, ativo, "
                "deve_trocar_senha, tentativas_falhas) VALUES "
                "(:id, 'dona@exemplo.com', 'Dona', 'CIDADAO', 'x', true, false, 0)"
            ),
            {"id": dona},
        )
        repositorio = PedidoAcompanhadoRepositorySql(sessao)
        repositorio.adicionar(dona, "2026/1", AGORA)
        repositorio.adicionar(dona, "2026/2", AGORA)

    with fabrica.begin() as sessao:
        repositorio = PedidoAcompanhadoRepositorySql(sessao)
        guardados = repositorio.listar(dona)
        repositorio.remover_todos(dona)
        sobra = repositorio.listar(dona)

    assert sorted(item.protocolo for item in guardados) == ["2026/1", "2026/2"]
    assert sobra == []
