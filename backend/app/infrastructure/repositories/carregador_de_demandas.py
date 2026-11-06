from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import islice
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.application.portas.importacoes import (
    ComparacaoComABase,
    ContribuicoesARetirar,
    PaginaDeRegistros,
    PlanoDeCarga,
    RegistroImportado,
    ResultadoDaCarga,
)
from app.domain.importacao.decisoes import PoliticaDeRepetidos
from app.domain.importacao.registro import RegistroDeDemanda

TAMANHO_DO_LOTE = 50_000
COLUNAS = RegistroDeDemanda._fields
COLUNAS_DA_FATO = ", ".join(("importacao_id", *COLUNAS))
COLUNAS_DA_CARGA = ", ".join(COLUNAS)
COLUNAS_ATUALIZAVEIS = [
    coluna for coluna in COLUNAS if coluna not in ("chave_registro", "id_local", "numero_informado")
]
ATRIBUICOES = ",\n    ".join(f"{coluna} = c.{coluna}" for coluna in COLUNAS_ATUALIZAVEIS)
COLUNAS_DA_TABELA = f"importacao_id, {COLUNAS_DA_CARGA}"

CRIAR_CARGA = """
CREATE TEMP TABLE carga (LIKE ouro.fato_demanda) ON COMMIT DROP;
ALTER TABLE carga ALTER COLUMN importacao_id DROP NOT NULL;
"""
INSERIR_NOVOS = f"""
INSERT INTO ouro.fato_demanda ({COLUNAS_DA_FATO})
SELECT :importacao_id, {COLUNAS_DA_CARGA} FROM carga
ON CONFLICT (chave_registro) DO NOTHING
"""
CONTAR_ALTERADOS = """
SELECT count(*) FROM carga c
JOIN ouro.fato_demanda f USING (chave_registro)
WHERE f.assinatura <> c.assinatura AND f.importacao_id <> :importacao_id
"""
GUARDAR_VERSAO_ANTERIOR = f"""
INSERT INTO ouro.fato_demanda_substituida (substituida_por, {COLUNAS_DA_TABELA})
SELECT :importacao_id, {", ".join(f"f.{coluna}" for coluna in ("importacao_id", *COLUNAS))}
FROM ouro.fato_demanda f
JOIN carga c USING (chave_registro)
WHERE f.assinatura <> c.assinatura AND f.importacao_id <> :importacao_id
"""
ATUALIZAR_ALTERADOS = f"""
UPDATE ouro.fato_demanda f SET
    importacao_id = :importacao_id,
    id_local = coalesce(c.id_local, f.id_local),
    numero_informado = coalesce(c.numero_informado, f.numero_informado),
    {ATRIBUICOES}
FROM carga c
WHERE f.chave_registro = c.chave_registro
    AND f.assinatura <> c.assinatura AND f.importacao_id <> :importacao_id
"""
GUARDAR_RETIRADAS = f"""
INSERT INTO ouro.fato_demanda_substituida (substituida_por, {COLUNAS_DA_TABELA})
SELECT :importacao_id, {COLUNAS_DA_TABELA} FROM ouro.fato_demanda
WHERE chave_registro = ANY(:chaves)
"""
APAGAR_RETIRADAS = "DELETE FROM ouro.fato_demanda WHERE chave_registro = ANY(:chaves)"
MARCAR_RETIRADAS = """
UPDATE app.contribuicao SET retirada_por = :importacao_id WHERE id = ANY(:ids)
"""
APAGAR_DA_IMPORTACAO = "DELETE FROM ouro.fato_demanda WHERE importacao_id = :importacao_id"
RESTAURAR_VERSOES_ANTERIORES = f"""
INSERT INTO ouro.fato_demanda ({COLUNAS_DA_TABELA})
SELECT {COLUNAS_DA_TABELA} FROM ouro.fato_demanda_substituida
WHERE substituida_por = :importacao_id
"""
APAGAR_VERSOES_ANTERIORES = """
DELETE FROM ouro.fato_demanda_substituida WHERE substituida_por = :importacao_id
"""
LISTAR_REGISTROS = """
SELECT
    fonte, ano, data_abertura, data_ult_movimento, dias_ate_movimento, categoria, servico, orgao,
    bairro_oficial, rpa, situacao
FROM ouro.fato_demanda
WHERE importacao_id = :importacao_id
ORDER BY data_abertura DESC NULLS LAST, chave_registro
LIMIT :limite OFFSET :deslocamento
"""
CONTAR_REGISTROS = "SELECT count(*) FROM ouro.fato_demanda WHERE importacao_id = :importacao_id"


def _em_lotes[T](itens: Iterable[T], tamanho: int) -> Iterator[list[T]]:
    fluxo = iter(itens)
    while lote := list(islice(fluxo, tamanho)):
        yield lote


def _copiar(sessao: Session, comando: str, linhas: Iterable[tuple[Any, ...]]) -> None:
    conexao = sessao.connection().connection.driver_connection
    assert conexao is not None  # noqa: S101
    with conexao.cursor() as cursor, cursor.copy(comando) as copia:
        for linha in linhas:
            copia.write_row(linha)


@dataclass
class _Contagem:
    novas: int = 0
    atualizadas: int = 0
    iguais: int = 0
    ignoradas: int = 0

    def somar_lote(self, tamanho: int, novas: int, alteradas: int, atualizou: bool) -> None:
        self.novas += novas
        self.atualizadas += alteradas if atualizou else 0
        self.ignoradas += 0 if atualizou else alteradas
        self.iguais += tamanho - novas - alteradas


class CarregadorSql:
    """Grava em lotes numa transação só: uma falha no meio não deixa carga pela metade."""

    def __init__(self, fabrica: sessionmaker[Session]) -> None:
        self._fabrica = fabrica

    def comparar_com_a_base(self, assinaturas: Iterable[tuple[int, int]]) -> ComparacaoComABase:
        iguais = alteradas = 0
        with self._fabrica.begin() as sessao:
            sessao.execute(
                text(
                    "CREATE TEMP TABLE comparacao (chave_registro bigint, assinatura bigint) "
                    "ON COMMIT DROP"
                )
            )
            for lote in _em_lotes(assinaturas, TAMANHO_DO_LOTE):
                _copiar(sessao, "COPY comparacao FROM STDIN", lote)
                linha = sessao.execute(
                    text(
                        "SELECT count(*) FILTER (WHERE f.assinatura = c.assinatura), "
                        "count(*) FILTER (WHERE f.assinatura <> c.assinatura) "
                        "FROM comparacao c JOIN ouro.fato_demanda f USING (chave_registro)"
                    )
                ).one()
                iguais += linha[0]
                alteradas += linha[1]
                sessao.execute(text("TRUNCATE comparacao"))
        return ComparacaoComABase(iguais, alteradas)

    def carregar(
        self, importacao_id: int, registros: Iterable[RegistroDeDemanda], plano: PlanoDeCarga
    ) -> ResultadoDaCarga:
        contagem = _Contagem()
        atualizar = plano.politica is PoliticaDeRepetidos.ATUALIZAR
        parametros = {"importacao_id": importacao_id}
        with self._fabrica.begin() as sessao:
            sessao.execute(text(CRIAR_CARGA))
            for lote in _em_lotes(registros, TAMANHO_DO_LOTE):
                _copiar(sessao, f"COPY carga ({COLUNAS_DA_CARGA}) FROM STDIN", lote)
                alteradas = sessao.scalar(text(CONTAR_ALTERADOS), parametros) or 0
                novas = sessao.execute(text(INSERIR_NOVOS), parametros).rowcount  # type: ignore[attr-defined]
                if atualizar and alteradas:
                    sessao.execute(text(GUARDAR_VERSAO_ANTERIOR), parametros)
                    sessao.execute(text(ATUALIZAR_ALTERADOS), parametros)
                contagem.somar_lote(len(lote), novas, alteradas, atualizar)
                sessao.execute(text("TRUNCATE carga"))
            self._retirar(sessao, importacao_id, plano.retirada)
        return ResultadoDaCarga(
            contagem.novas,
            contagem.atualizadas,
            contagem.iguais,
            contagem.ignoradas,
            len(plano.retirada.ids),
        )

    @staticmethod
    def _retirar(sessao: Session, importacao_id: int, retirada: ContribuicoesARetirar) -> None:
        """A versão retirada vai para a tabela que o desfazer já restaura."""
        if not retirada.ids:
            return
        chaves = {"importacao_id": importacao_id, "chaves": list(retirada.chaves)}
        sessao.execute(text(GUARDAR_RETIRADAS), chaves)
        sessao.execute(text(APAGAR_RETIRADAS), chaves)
        sessao.execute(
            text(MARCAR_RETIRADAS), {"importacao_id": importacao_id, "ids": list(retirada.ids)}
        )

    def desfazer(self, importacao_id: int) -> None:
        parametros = {"importacao_id": importacao_id}
        with self._fabrica.begin() as sessao:
            sessao.execute(text(APAGAR_DA_IMPORTACAO), parametros)
            sessao.execute(text(RESTAURAR_VERSOES_ANTERIORES), parametros)
            sessao.execute(text(APAGAR_VERSOES_ANTERIORES), parametros)

    def listar_registros(
        self, importacao_id: int, limite: int, deslocamento: int
    ) -> PaginaDeRegistros:
        parametros = {
            "importacao_id": importacao_id,
            "limite": limite,
            "deslocamento": deslocamento,
        }
        with self._fabrica() as sessao:
            linhas = sessao.execute(text(LISTAR_REGISTROS), parametros).all()
            total = sessao.scalar(text(CONTAR_REGISTROS), parametros) or 0
        return PaginaDeRegistros([RegistroImportado(*linha) for linha in linhas], total)
