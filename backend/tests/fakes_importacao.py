from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field, replace
from pathlib import Path

from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.importacoes import (
    ArquivoRecebido,
    ComparacaoComABase,
    FiltroDeImportacoes,
    NovaImportacao,
    PaginaDeImportacoes,
    PaginaDeRegistros,
    ResultadoDaCarga,
)
from app.domain.importacao.decisoes import PoliticaDeRepetidos
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.normalizador import Referencias
from app.domain.importacao.registro import RegistroDeDemanda
from tests.fakes import INICIO_DOS_TESTES, RelogioFixo

ARQUIVO = ArquivoRecebido("referencia", "156_2026.csv", 10, "a" * 64)


class ImportacoesEmMemoria:
    def __init__(self) -> None:
        self.itens: dict[int, Importacao] = {}

    def criar(self, nova: NovaImportacao, status: StatusDaImportacao) -> Importacao:
        importacao = Importacao(
            id=len(self.itens) + 1,
            nome_do_arquivo=nova.arquivo.nome,
            tamanho_em_bytes=nova.arquivo.tamanho_em_bytes,
            hash_do_arquivo=nova.arquivo.hash_do_arquivo,
            usuario_id=nova.usuario_id,
            status=status,
            criada_em=INICIO_DOS_TESTES,
            carga_inicial=nova.carga_inicial,
            estrutura={"referencia": nova.arquivo.referencia},
        )
        self.itens[importacao.id] = importacao
        return importacao

    def buscar(self, importacao_id: int) -> Importacao | None:
        return self.itens.get(importacao_id)

    def listar(self, filtro: FiltroDeImportacoes) -> PaginaDeImportacoes:
        return PaginaDeImportacoes(list(self.itens.values()), len(self.itens))

    def salvar(self, importacao: Importacao) -> None:
        self.itens[importacao.id] = importacao

    def atualizar_progresso(
        self, importacao_id: int, status: StatusDaImportacao, progresso: int
    ) -> None:
        self.itens[importacao_id] = replace(
            self.itens[importacao_id], status=status, progresso=progresso
        )

    def mesmo_arquivo(self, hash_do_arquivo: str, importacao_id: int) -> list[Importacao]:
        return [
            item
            for item in self.itens.values()
            if item.hash_do_arquivo == hash_do_arquivo and item.id != importacao_id
        ]

    def ultima_concluida(self) -> Importacao | None:
        concluidas = [
            item for item in self.itens.values() if item.status is StatusDaImportacao.CONCLUIDA
        ]
        return concluidas[-1] if concluidas else None

    def em_andamento(self) -> list[Importacao]:
        return [
            item
            for item in self.itens.values()
            if item.status in (StatusDaImportacao.ANALISANDO, StatusDaImportacao.ATUALIZANDO_PAINEL)
        ]


@dataclass(frozen=True)
class TabelaFalsa:
    colunas: list[str]
    dados: list[list[str]]
    formato: str = "csv"
    codificacao: str | None = "utf-8-sig"
    separador: str | None = ";"

    def linhas(self) -> Iterator[list[str]]:
        return iter(self.dados)


@dataclass
class LeitorFalso:
    tabela: TabelaFalsa

    def abrir(self, caminho: Path) -> TabelaFalsa:
        return self.tabela


@dataclass
class ArmazenamentoFalso:
    removidos: list[str] = field(default_factory=list)

    def iniciar_recebimento(self, nome: str) -> "ArmazenamentoFalso":
        return self

    def gravar(self, bloco: bytes) -> None:
        return None

    def concluir(self) -> ArquivoRecebido:
        return ARQUIVO

    def abandonar(self) -> None:
        return None

    def localizar(self, referencia: str) -> Path:
        return Path(referencia)

    def remover(self, referencia: str) -> None:
        self.removidos.append(referencia)


@dataclass
class CarregadorFalso:
    comparacao: ComparacaoComABase = field(default_factory=ComparacaoComABase)
    carregados: list[RegistroDeDemanda] = field(default_factory=list)
    desfeitas: list[int] = field(default_factory=list)

    def comparar_com_a_base(self, assinaturas: Iterable[tuple[int, int]]) -> ComparacaoComABase:
        list(assinaturas)
        return self.comparacao

    def carregar(
        self,
        importacao_id: int,
        registros: Iterable[RegistroDeDemanda],
        politica: PoliticaDeRepetidos,
    ) -> ResultadoDaCarga:
        self.carregados = list(registros)
        return ResultadoDaCarga(novas=len(self.carregados))

    def desfazer(self, importacao_id: int) -> None:
        self.desfeitas.append(importacao_id)

    def listar_registros(
        self, importacao_id: int, limite: int, deslocamento: int
    ) -> PaginaDeRegistros:
        return PaginaDeRegistros()


@dataclass
class AtualizadorFalso:
    chamadas: int = 0

    def atualizar(self, ao_avancar: Callable[[int], None]) -> None:
        self.chamadas += 1
        ao_avancar(100)


@dataclass
class ReferenciasFalsas:
    valor: Referencias = field(default_factory=lambda: Referencias({"AFOGADOS": "5"}, {}))

    def carregar(self) -> Referencias:
        return self.valor


class FilaImediataDeTeste:
    def enfileirar(self, tarefa: Callable[[], None]) -> None:
        tarefa()


def criar_servicos(tabela: TabelaFalsa) -> ServicosDeImportacao:
    return ServicosDeImportacao(
        importacoes=ImportacoesEmMemoria(),
        armazenamento=ArmazenamentoFalso(),
        leitor=LeitorFalso(tabela),
        carregador=CarregadorFalso(),
        atualizador=AtualizadorFalso(),
        referencias=ReferenciasFalsas(),
        fila=FilaImediataDeTeste(),
        relogio=RelogioFixo(),
    )
