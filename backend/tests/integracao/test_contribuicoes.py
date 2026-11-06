from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.contribuicoes.decidir_par import DecidirPar
from app.application.casos_de_uso.contribuicoes.expurgar_enderecos import ExpurgarEnderecos
from app.application.casos_de_uso.contribuicoes.gerar_pacote import GerarPacote
from app.application.casos_de_uso.contribuicoes.receber_contribuicao import ReceberContribuicao
from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.casos_de_uso.importacoes.cancelar_importacao import CancelarImportacao
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
from app.domain.contribuicao.contribuicao import (
    DecisaoDoPar,
    FormularioPreenchido,
    ResultadoDoEnvio,
    RetornoAnterior,
)
from app.domain.erros import PenteFinoPendente
from app.domain.fontes import Fonte
from app.domain.importacao.decisoes import PoliticaEntreCanais
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.pendencias import TipoDePendencia
from app.infrastructure.importacao.montagem import (
    FilaImediata,
    montar_servicos_de_contribuicoes,
    montar_servicos_de_importacao,
)
from app.infrastructure.settings import Configuracao
from tests.conftest import SEGREDO_DE_TESTE
from tests.fakes import criar_usuario
from tests.integracao.test_importacao_e_painel import (
    CABECALHO,
    URL_DO_BANCO_DE_TESTE,
    preparar_esquema,
)

pytestmark = pytest.mark.skipif(
    URL_DO_BANCO_DE_TESTE is None, reason="API_URL_DO_BANCO_DE_TESTE não configurada"
)

HOJE = datetime.now(UTC).date()
VIA = "Rua da Esperança Fictícia"


def formulario(chave: str, numero: str = "100") -> FormularioPreenchido:
    return FormularioPreenchido(
        chave_de_envio=chave * 16,
        servico_codigo="131",
        bairro_oficial="AFOGADOS",
        logradouro=VIA,
        numero=numero,
        detalhe="",
        retorno=RetornoAnterior.REGISTROU_SEM_RETORNO,
    )


def linha_do_156(data: date, numero: str = "100") -> str:
    via = "RUA DA ESPERANCA FICTICIA"
    fim = data.isoformat()
    return f"1;PAVIMENTACAO;131;OPERACAO TAPA-BURACO;{via};{numero};AFOGADOS;5;{fim};ATENDIDA;{fim}"


@dataclass
class Ambiente:
    servicos: ServicosDeContribuicoes
    fabrica: sessionmaker[Session]
    pasta: Path
    usuario_id: object

    @property
    def importacao(self) -> ServicosDeImportacao:
        return self.servicos.importacao

    def contar(self, consulta: str) -> int:
        with self.fabrica() as sessao:
            return sessao.scalar(text(consulta)) or 0

    def gerar_pacote(self) -> Importacao:
        pacote = GerarPacote(self.servicos).executar(self.usuario_id)  # type: ignore[arg-type]
        return self.importacao.obter(pacote.id)

    def confirmar(self, importacao: Importacao) -> Importacao:
        ConfirmarImportacao(self.importacao).executar(importacao.id)
        return self.importacao.obter(importacao.id)

    def importar_arquivo(self, nome: str, linhas: list[str]) -> Importacao:
        caminho = self.pasta / nome
        caminho.write_text("\n".join([CABECALHO, *linhas]), encoding="utf-8")
        recebimento = self.importacao.armazenamento.iniciar_recebimento(caminho.name)
        recebimento.gravar(caminho.read_bytes())
        importacao = ReceberArquivo(self.importacao).executar(
            recebimento.concluir(),
            self.usuario_id,  # type: ignore[arg-type]
        )
        analisada = self.importacao.obter(importacao.id)
        escolha = EscolhaDeColunas(
            Fonte.CENTRAL_156,
            HOJE,
            dict(analisada.decisoes.mapeamento),
            dict(analisada.decisoes.valores_fixos),
        )
        DefinirColunas(self.importacao).executar(importacao.id, escolha)
        return self.importacao.obter(importacao.id)

    def responder(self, importacao: Importacao, respostas: RespostasDePendencias) -> Importacao:
        ResponderPendencias(self.importacao).executar(importacao.id, respostas)
        return self.importacao.obter(importacao.id)


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
    importacao = montar_servicos_de_importacao(configuracao, fabrica, FilaImediata())
    yield Ambiente(
        montar_servicos_de_contribuicoes(fabrica, importacao), fabrica, tmp_path, usuario.id
    )
    motor.dispose()


def test_relato_nao_aparece_no_painel_antes_da_revisao(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))

    assert ambiente.contar("SELECT count(*) FROM app.contribuicao") == 1
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 0


def test_duas_pessoas_viram_uma_linha_na_base(ambiente: Ambiente) -> None:
    receber = ReceberContribuicao(ambiente.servicos)
    receber.executar(formulario("a"))
    assert receber.executar(formulario("b")) is ResultadoDoEnvio.SOMADA

    pacote = ambiente.gerar_pacote()

    assert pacote.status is StatusDaImportacao.PRONTA
    final = ambiente.confirmar(pacote)
    assert final.status is StatusDaImportacao.CONCLUIDA
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1
    resumo = ambiente.servicos.contribuicoes.resumir()
    assert (resumo.relatos, resumo.ocorrencias, resumo.somados, resumo.na_base) == (2, 1, 1, 1)


def test_endereco_e_detalhe_nunca_chegam_a_base_analitica(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))

    ambiente.confirmar(ambiente.gerar_pacote())

    with ambiente.fabrica() as sessao:
        linha = sessao.execute(text("SELECT * FROM ouro.fato_demanda")).one()
        historico = sessao.execute(text("SELECT pendencias, resultado FROM app.importacao")).one()
    assert "ESPERANCA" not in str(linha)
    assert "ESPERANCA" not in str(historico)


def test_par_em_aberto_trava_o_pacote_ate_a_decisao(ambiente: Ambiente) -> None:
    receber = ReceberContribuicao(ambiente.servicos)
    receber.executar(formulario("a"))
    assert receber.executar(formulario("b", "110")) is ResultadoDoEnvio.EM_CONFERENCIA

    with pytest.raises(PenteFinoPendente):
        ambiente.gerar_pacote()

    par = ambiente.servicos.contribuicoes.listar_pares_abertos(10)[0]
    DecidirPar(ambiente.servicos).executar(
        par.id,
        DecisaoDoPar.MESMA,
        ambiente.usuario_id,  # type: ignore[arg-type]
    )
    ambiente.confirmar(ambiente.gerar_pacote())
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1


def test_par_decidido_como_diferente_mantem_as_duas(ambiente: Ambiente) -> None:
    receber = ReceberContribuicao(ambiente.servicos)
    receber.executar(formulario("a"))
    receber.executar(formulario("b", "110"))
    par = ambiente.servicos.contribuicoes.listar_pares_abertos(10)[0]

    DecidirPar(ambiente.servicos).executar(
        par.id,
        DecisaoDoPar.DIFERENTE,
        ambiente.usuario_id,  # type: ignore[arg-type]
    )

    ambiente.confirmar(ambiente.gerar_pacote())
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 2


def test_importacao_manual_para_quando_coincide_com_relato_ja_carregado(
    ambiente: Ambiente,
) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    ambiente.confirmar(ambiente.gerar_pacote())

    manual = ambiente.importar_arquivo("156_2026.csv", [linha_do_156(HOJE)])

    assert manual.status is StatusDaImportacao.AGUARDANDO_DECISOES
    tipos = [item["tipo"] for item in manual.pendencias["itens"]]
    assert tipos == [TipoDePendencia.COINCIDENCIAS_CERTAS]
    assert manual.pendencias["resumo"]["pente_fino"]["certas"] == 1
    assert "ESPERANCA" not in str(manual.pendencias)


def test_manter_o_oficial_tira_o_relato_e_desfazer_devolve(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    ambiente.confirmar(ambiente.gerar_pacote())
    manual = ambiente.importar_arquivo("156_2026.csv", [linha_do_156(HOJE)])

    pronta = ambiente.responder(
        manual,
        RespostasDePendencias(coincidencias_certas=PoliticaEntreCanais.MANTER_O_REGISTRO_OFICIAL),
    )
    final = ambiente.confirmar(pronta)

    assert final.resultado["retiradas"] == 1
    consulta_formulario = (
        "SELECT count(*) FROM ouro.fato_demanda WHERE fonte = 'FORMULARIO_PUBLICO'"
    )
    assert ambiente.contar(consulta_formulario) == 0
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1
    assert ambiente.servicos.contribuicoes.resumir().retiradas == 1

    DesfazerImportacao(ambiente.importacao).executar(final.id)

    assert ambiente.contar(consulta_formulario) == 1
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1
    assert ambiente.servicos.contribuicoes.resumir().retiradas == 0


def test_manter_os_dois_preserva_o_relato(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    ambiente.confirmar(ambiente.gerar_pacote())
    manual = ambiente.importar_arquivo("156_2026.csv", [linha_do_156(HOJE)])

    pronta = ambiente.responder(
        manual, RespostasDePendencias(coincidencias_certas=PoliticaEntreCanais.MANTER_OS_DOIS)
    )
    ambiente.confirmar(pronta)

    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 2


def test_relato_ainda_em_quarentena_tambem_e_conferido(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))

    manual = ambiente.importar_arquivo("156_2026.csv", [linha_do_156(HOJE)])
    pronta = ambiente.responder(
        manual,
        RespostasDePendencias(coincidencias_certas=PoliticaEntreCanais.MANTER_O_REGISTRO_OFICIAL),
    )
    ambiente.confirmar(pronta)

    assert ambiente.servicos.contribuicoes.prontas_para_pacote() == []


def test_mesmo_local_depois_de_30_dias_e_reincidencia_e_nao_trava(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    antigo = HOJE - timedelta(days=30)

    manual = ambiente.importar_arquivo("156_2026.csv", [linha_do_156(antigo)])

    assert manual.status is StatusDaImportacao.PRONTA
    assert manual.pendencias["resumo"]["pente_fino"]["certas"] == 0


def test_pacote_e_conferido_com_o_que_ja_esta_na_base(ambiente: Ambiente) -> None:
    ambiente.confirmar(ambiente.importar_arquivo("156_2026.csv", [linha_do_156(HOJE)]))
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))

    pacote = ambiente.gerar_pacote()

    assert pacote.status is StatusDaImportacao.AGUARDANDO_DECISOES
    pronta = ambiente.responder(
        pacote,
        RespostasDePendencias(coincidencias_certas=PoliticaEntreCanais.MANTER_O_REGISTRO_OFICIAL),
    )
    final = ambiente.confirmar(pronta)
    assert final.resultado["novas"] == 0
    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1


def test_cancelar_o_pacote_devolve_os_relatos_a_fila(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    pacote = ambiente.gerar_pacote()
    assert ambiente.servicos.contribuicoes.prontas_para_pacote() == []

    CancelarImportacao(ambiente.importacao).executar(pacote.id)

    assert len(ambiente.servicos.contribuicoes.prontas_para_pacote()) == 1


def test_desfazer_o_pacote_tira_da_base_e_devolve_a_fila(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    final = ambiente.confirmar(ambiente.gerar_pacote())

    DesfazerImportacao(ambiente.importacao).executar(final.id)

    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 0
    assert len(ambiente.servicos.contribuicoes.prontas_para_pacote()) == 1


def test_gerar_o_pacote_de_novo_nao_duplica(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    final = ambiente.confirmar(ambiente.gerar_pacote())
    DesfazerImportacao(ambiente.importacao).executar(final.id)

    ambiente.confirmar(ambiente.gerar_pacote())

    assert ambiente.contar("SELECT count(*) FROM ouro.fato_demanda") == 1


def test_expurgo_apaga_endereco_e_detalhe_e_mantem_o_pseudonimo(ambiente: Ambiente) -> None:
    ReceberContribuicao(ambiente.servicos).executar(formulario("a"))
    with ambiente.fabrica.begin() as sessao:
        sessao.execute(
            text("UPDATE app.contribuicao SET recebida_em = recebida_em - interval '91 days'")
        )

    apagadas = ExpurgarEnderecos(
        ambiente.servicos.contribuicoes, ambiente.servicos.relogio
    ).executar()

    assert apagadas == 1
    assert ambiente.contar("SELECT count(*) FROM app.contribuicao WHERE logradouro IS NULL") == 1
    assert ambiente.contar("SELECT count(*) FROM app.contribuicao WHERE id_local IS NOT NULL") == 1
