import json
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.importacoes.confirmar_importacao import ConfirmarImportacao
from app.application.casos_de_uso.importacoes.definir_colunas import (
    DefinirColunas,
    EscolhaDeColunas,
)
from app.application.casos_de_uso.importacoes.desfazer_importacao import DesfazerImportacao
from app.application.casos_de_uso.importacoes.receber_arquivo import ReceberArquivo
from app.application.casos_de_uso.importacoes.responder_pendencias import (
    ResponderPendencias,
    RespostasDePendencias,
)
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.importacao.decisoes import ACEITAR_COMO_NOVO, PoliticaDeRepetidos
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.infrastructure.importacao.montagem import FilaImediata, montar_servicos_de_importacao
from app.infrastructure.repositories.prazos import PrazoRepositorySql
from app.infrastructure.repositories.recorrencias import RecorrenciaRepositorySql
from app.infrastructure.repositories.visao_geral import VisaoGeralRepositorySql
from app.infrastructure.settings import Configuracao
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import criar_usuario


class ConfiguracaoDosTestes(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    url_do_banco_de_teste: str | None = None


URL_DO_BANCO_DE_TESTE = ConfiguracaoDosTestes().url_do_banco_de_teste
RAIZ_DO_BACKEND = Path(__file__).resolve().parents[2]
CABECALHO = (
    "GRUPOSERVICO_CODIGO;GRUPOSERVICO_DESCRICAO;SERVICO_CODIGO;SERVICO_DESCRICAO;LOGRADOURO;"
    "NUMERO;BAIRRO;RPA;DATA_DEMANDA;SITUACAO;DATA_ULT_SITUACAO"
)
RETRATO = date(2026, 10, 7)
SITUACAO_NOVA_ACEITA = {"situacao": {"ATENDIDA": ACEITAR_COMO_NOVO}}

pytestmark = pytest.mark.skipif(
    not URL_DO_BANCO_DE_TESTE, reason="API_URL_DO_BANCO_DE_TESTE não definida"
)


def linha(servico: str, data: str, situacao: str = "ATENDIDA", fim: str = "") -> str:
    fim = fim or data
    return f"1;DRENAGEM;{servico};Limpeza;RUA DO TESTE;10;AFOGADOS;5;{data};{situacao};{fim}"


def arquivo_156(tmp_path: Path, nome: str, linhas: list[str]) -> Path:
    caminho = tmp_path / nome
    caminho.write_text("\n".join([CABECALHO, *linhas]), encoding="utf-8")
    return caminho


@dataclass
class Ambiente:
    servicos: ServicosDeImportacao
    fabrica: sessionmaker[Session]
    pasta: Path
    usuario_id: object

    def importar(self, caminho: Path) -> Importacao:
        recebimento = self.servicos.armazenamento.iniciar_recebimento(caminho.name)
        recebimento.gravar(caminho.read_bytes())
        importacao = ReceberArquivo(self.servicos).executar(
            recebimento.concluir(),
            self.usuario_id,  # type: ignore[arg-type]
        )
        analisada = self.servicos.obter(importacao.id)
        escolha = EscolhaDeColunas(
            Fonte.CENTRAL_156,
            RETRATO,
            dict(analisada.decisoes.mapeamento),
            dict(analisada.decisoes.valores_fixos),
        )
        DefinirColunas(self.servicos).executar(importacao.id, escolha)
        return self.servicos.obter(importacao.id)

    def confirmar(self, importacao: Importacao) -> Importacao:
        ConfirmarImportacao(self.servicos).executar(importacao.id)
        return self.servicos.obter(importacao.id)

    def contar(self, consulta: str) -> int:
        with self.fabrica() as sessao:
            return sessao.scalar(text(consulta)) or 0


def preparar_esquema(url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    motor = create_engine(url)
    with motor.begin() as conexao:
        conexao.execute(text("DROP SCHEMA IF EXISTS ouro CASCADE"))
        conexao.execute(text("DROP SCHEMA IF EXISTS app CASCADE"))
        conexao.execute(text("DROP TABLE IF EXISTS alembic_version"))
    motor.dispose()
    monkeypatch.setenv("API_URL_DO_BANCO", url)
    monkeypatch.chdir(RAIZ_DO_BACKEND)
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture
def ambiente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Ambiente]:
    assert URL_DO_BANCO_DE_TESTE
    preparar_esquema(URL_DO_BANCO_DE_TESTE, monkeypatch)
    motor = create_engine(URL_DO_BANCO_DE_TESTE)
    fabrica = sessionmaker(motor, expire_on_commit=False)
    configuracao = Configuracao(
        url_do_banco=URL_DO_BANCO_DE_TESTE,
        segredo_jwt=SecretStr(SEGREDO_DE_TESTE),
        pasta_das_importacoes=tmp_path / "importacoes",
        sal_do_id_local=SecretStr("sal-de-teste"),
    )
    usuario = criar_usuario()
    with fabrica.begin() as sessao:
        sessao.execute(
            text(
                "INSERT INTO app.usuario (id, email, nome, perfil, hash_da_senha, ativo, "
                "deve_trocar_senha, tentativas_falhas) VALUES "
                "(:id, :email, 'Teste', 'GESTOR', 'x', true, false, 0)"
            ),
            {"id": usuario.id, "email": f"{uuid4().hex}@recife.pe.gov.br"},
        )
    servicos = montar_servicos_de_importacao(configuracao, fabrica, FilaImediata())
    yield Ambiente(servicos, fabrica, tmp_path, usuario.id)
    motor.dispose()


def test_arquivo_entra_na_base_e_atualiza_as_views(ambiente: Ambiente, tmp_path: Path) -> None:
    caminho = arquivo_156(
        tmp_path,
        "156_2024.csv",
        [linha("10", "2024-03-01", fim="2024-03-05"), linha("11", "2024-03-02", fim="2024-03-02")],
    )

    final = ambiente.confirmar(ambiente.importar(caminho))

    assert final.status is StatusDaImportacao.CONCLUIDA
    assert final.resultado["novas"] == 2
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 2
    assert ambiente.contar("SELECT sum(n) FROM ouro.mv_demanda") == 2
    assert ambiente.contar("SELECT sum(n) FROM ouro.mv_prazos_156") == 2


def test_endereco_nunca_chega_ao_banco(ambiente: Ambiente, tmp_path: Path) -> None:
    caminho = arquivo_156(tmp_path, "156_2024.csv", [linha("10", "2024-03-01")])

    final = ambiente.confirmar(ambiente.importar(caminho))

    with ambiente.fabrica() as sessao:
        linha_salva = sessao.execute(text("SELECT * FROM ouro.fato_demanda")).one()
        historico = sessao.execute(
            text("SELECT estrutura, decisoes, pendencias, resultado FROM app.importacao")
        ).one()
    assert "RUA DO TESTE" not in str(linha_salva)
    assert "RUA DO TESTE" not in json.dumps([*historico])
    assert final.arquivo_guardado is False
    assert not list((tmp_path / "importacoes").iterdir())


def test_reimportar_o_mesmo_arquivo_nao_duplica(ambiente: Ambiente, tmp_path: Path) -> None:
    caminho = arquivo_156(tmp_path, "156_2024.csv", [linha("10", "2024-03-01")])
    ambiente.confirmar(ambiente.importar(caminho))

    segunda = ambiente.importar(caminho)

    assert segunda.status is StatusDaImportacao.PRONTA
    assert segunda.pendencias["resumo"]["iguais"] == 1
    final = ambiente.confirmar(segunda)
    assert final.resultado["novas"] == 0
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1


def test_arquivo_novo_atualiza_e_desfazer_restaura(ambiente: Ambiente, tmp_path: Path) -> None:
    antigo = arquivo_156(
        tmp_path, "156_2025.csv", [linha("10", "2025-03-01", "EXECUCAO", "2025-03-02")]
    )
    ambiente.confirmar(ambiente.importar(antigo))
    novo = arquivo_156(
        tmp_path, "156_republicado_2025.csv", [linha("10", "2025-03-01", "ATENDIDA", "2025-04-01")]
    )

    importacao = ambiente.importar(novo)
    assert importacao.status is StatusDaImportacao.AGUARDANDO_DECISOES
    respostas = RespostasDePendencias(
        repetidos_na_base=PoliticaDeRepetidos.ATUALIZAR, substituicoes=SITUACAO_NOVA_ACEITA
    )
    ResponderPendencias(ambiente.servicos).executar(importacao.id, respostas)
    final = ambiente.confirmar(ambiente.servicos.obter(importacao.id))

    assert final.resultado["atualizadas"] == 1
    consulta = "SELECT count(*) FROM ouro.fato_demanda WHERE situacao = 'ATENDIDA'"
    assert ambiente.contar(consulta) == 1

    DesfazerImportacao(ambiente.servicos).executar(final.id)

    assert ambiente.contar(consulta) == 0
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda_substituida") == 0


def test_arquivo_de_outro_ano_nao_substitui_a_linha_do_ano_anterior(
    ambiente: Ambiente, tmp_path: Path
) -> None:
    antigo = arquivo_156(tmp_path, "156_2025.csv", [linha("10", "2025-03-01", "EXECUCAO")])
    ambiente.confirmar(ambiente.importar(antigo))
    novo = arquivo_156(tmp_path, "156_2026.csv", [linha("10", "2025-03-01", "EXECUCAO")])

    final = ambiente.confirmar(ambiente.importar(novo))

    assert final.resultado["novas"] == 1
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 2


def test_manter_atuais_nao_mexe_na_base(ambiente: Ambiente, tmp_path: Path) -> None:
    antigo = arquivo_156(tmp_path, "156_2025.csv", [linha("10", "2025-03-01", "EXECUCAO")])
    ambiente.confirmar(ambiente.importar(antigo))
    novo = arquivo_156(
        tmp_path, "156_republicado_2025.csv", [linha("10", "2025-03-01", "ATENDIDA")]
    )

    importacao = ambiente.importar(novo)
    respostas = RespostasDePendencias(
        repetidos_na_base=PoliticaDeRepetidos.MANTER_ATUAIS, substituicoes=SITUACAO_NOVA_ACEITA
    )
    ResponderPendencias(ambiente.servicos).executar(importacao.id, respostas)
    final = ambiente.confirmar(ambiente.servicos.obter(importacao.id))

    assert final.resultado["ignoradas"] == 1
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda WHERE situacao='ATENDIDA'") == 0


def test_percentis_seguem_a_regra_de_frequencia_acumulada(
    ambiente: Ambiente, tmp_path: Path
) -> None:
    linhas = [linha(str(dia), "2024-03-01", fim=f"2024-03-{dia + 1:02d}") for dia in range(1, 11)]
    ambiente.confirmar(ambiente.importar(arquivo_156(tmp_path, "156_2024.csv", linhas)))

    with ambiente.fabrica() as sessao:
        prazos = PrazoRepositorySql(sessao).resumo(Filtros(2024, 2024), sem_mesmo_dia=False)
        visao = VisaoGeralRepositorySql(sessao).percentis_de_prazo(Filtros(2024, 2024))

    assert prazos.pedidos == 10
    assert prazos.mediana == 5
    assert prazos.p90 == 9
    assert visao.mediana == 5


def test_repeticao_separa_duplicidade_de_reincidencia(ambiente: Ambiente, tmp_path: Path) -> None:
    linhas = [
        linha("10", "2024-01-01"),
        linha("10", "2024-01-05"),
        linha("10", "2024-03-01"),
    ]
    ambiente.confirmar(ambiente.importar(arquivo_156(tmp_path, "156_2024.csv", linhas)))

    with ambiente.fabrica() as sessao:
        pedidos, repetidos, intervalos = RecorrenciaRepositorySql(sessao).totais(
            Filtros(2024, 2024), sem_generico=False
        )

    assert pedidos == 3
    assert repetidos == 3
    assert intervalos.duplicidade == 1
    assert intervalos.reincidencia == 1
