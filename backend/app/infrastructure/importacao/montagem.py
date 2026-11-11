from collections.abc import Callable

from sqlalchemy.orm import Session, sessionmaker

from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import FilaDeImportacoes, OrigensDeDados
from app.infrastructure.contribuicoes.limite_em_memoria import LimiteEmMemoria
from app.infrastructure.importacao.armazenamento_local import ArmazenamentoLocal
from app.infrastructure.importacao.leitores import LeitorDeArquivos
from app.infrastructure.importacao.origens import DownloadPorHttps, ExtracaoDeBanco
from app.infrastructure.relogio import RelogioDoSistema
from app.infrastructure.repositories.atualizador_do_painel import AtualizadorDoPainelSql
from app.infrastructure.repositories.carregador_de_demandas import CarregadorSql
from app.infrastructure.repositories.contribuicoes import (
    ContribuicaoRepositorySql,
    ReferenciaDoFormularioSql,
)
from app.infrastructure.repositories.importacoes import ImportacaoRepositorySql
from app.infrastructure.repositories.referencias import ReferenciasSql
from app.infrastructure.settings import Configuracao


class FilaImediata:
    """Executa na hora: serve ao terminal, que espera a tarefa terminar."""

    def enfileirar(self, tarefa: Callable[[], None]) -> None:
        tarefa()


def montar_servicos_de_importacao(
    configuracao: Configuracao, fabrica: sessionmaker[Session], fila: FilaDeImportacoes
) -> ServicosDeImportacao:
    relogio = RelogioDoSistema()
    sal = configuracao.sal_do_id_local
    return ServicosDeImportacao(
        importacoes=ImportacaoRepositorySql(fabrica, relogio),
        armazenamento=ArmazenamentoLocal(
            configuracao.pasta_das_importacoes, configuracao.limite_da_importacao_em_bytes
        ),
        leitor=LeitorDeArquivos(),
        carregador=CarregadorSql(fabrica),
        atualizador=AtualizadorDoPainelSql(fabrica.kw["bind"]),
        referencias=ReferenciasSql(fabrica),
        fila=fila,
        relogio=relogio,
        contribuicoes=ContribuicaoRepositorySql(fabrica),
        sal=sal.get_secret_value() if sal else None,
    )


def montar_origens_de_dados(
    configuracao: Configuracao, servicos: ServicosDeImportacao
) -> OrigensDeDados:
    return OrigensDeDados(
        por_endereco=DownloadPorHttps(servicos.armazenamento, configuracao.hosts_de_importacao),
        por_banco=ExtracaoDeBanco(
            servicos.armazenamento,
            configuracao.bancos_de_origem,
            configuracao.segundos_da_extracao,
        ),
    )


def montar_servicos_de_contribuicoes(
    fabrica: sessionmaker[Session], importacao: ServicosDeImportacao
) -> ServicosDeContribuicoes:
    relogio = RelogioDoSistema()
    return ServicosDeContribuicoes(
        contribuicoes=ContribuicaoRepositorySql(fabrica),
        referencia=ReferenciaDoFormularioSql(fabrica),
        limite=LimiteEmMemoria(relogio),
        relogio=relogio,
        importacao=importacao,
        sal=importacao.sal,
    )
