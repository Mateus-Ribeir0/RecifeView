from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Protocol
from uuid import UUID

from app.domain.contribuicao.conferencia import RelatoGuardado, ResultadoDaConferencia
from app.domain.importacao.decisoes import PoliticaDeRepetidos
from app.domain.importacao.importacao import Importacao, StatusDaImportacao
from app.domain.importacao.normalizador import Referencias
from app.domain.importacao.registro import EnderecoDaLinha, RegistroDeDemanda


@dataclass(frozen=True)
class ArquivoRecebido:
    referencia: str
    nome: str
    tamanho_em_bytes: int
    hash_do_arquivo: str


@dataclass(frozen=True)
class NovaImportacao:
    arquivo: ArquivoRecebido
    usuario_id: UUID | None
    carga_inicial: bool = False


@dataclass(frozen=True)
class FiltroDeImportacoes:
    busca: str | None = None
    status: str | None = None
    fonte: str | None = None
    limite: int = 50
    deslocamento: int = 0


@dataclass(frozen=True)
class PaginaDeImportacoes:
    itens: list[Importacao]
    total: int


@dataclass(frozen=True)
class ComparacaoComABase:
    iguais: int = 0
    alteradas: int = 0


@dataclass(frozen=True)
class ResultadoDaCarga:
    novas: int = 0
    atualizadas: int = 0
    iguais: int = 0
    ignoradas: int = 0
    retiradas: int = 0


@dataclass(frozen=True)
class ContribuicoesARetirar:
    """Relatos que a pessoa decidiu tirar porque o registro oficial cobre a mesma demanda."""

    ids: tuple[UUID, ...] = ()
    chaves: tuple[int, ...] = ()


@dataclass(frozen=True)
class PlanoDeCarga:
    politica: PoliticaDeRepetidos
    retirada: ContribuicoesARetirar = field(default_factory=ContribuicoesARetirar)


@dataclass(frozen=True)
class RegistroNoMesmoLocal:
    fonte: str
    id_local: str
    categoria: str | None
    servico_codigo: str | None
    bairro_oficial: str | None
    data_abertura: date
    numero_informado: bool


@dataclass(frozen=True)
class RegistroImportado:
    fonte: str
    ano: int | None
    data_abertura: date | None
    data_ult_movimento: date | None
    dias_ate_movimento: int | None
    categoria: str | None
    servico: str | None
    orgao: str | None
    bairro_oficial: str | None
    rpa: str | None
    situacao: str | None


@dataclass(frozen=True)
class PaginaDeRegistros:
    itens: list[RegistroImportado] = field(default_factory=list)
    total: int = 0


class TabelaDoArquivo(Protocol):
    @property
    def formato(self) -> str: ...

    @property
    def codificacao(self) -> str | None: ...

    @property
    def separador(self) -> str | None: ...

    @property
    def colunas(self) -> list[str]: ...

    def linhas(self) -> Iterator[list[str]]: ...


class LeitorDeTabelas(Protocol):
    def abrir(self, caminho: Path) -> TabelaDoArquivo: ...


class RecebimentoDeArquivo(Protocol):
    def gravar(self, bloco: bytes) -> None: ...

    def concluir(self) -> ArquivoRecebido: ...

    def abandonar(self) -> None: ...


class ArmazenamentoDeArquivos(Protocol):
    def iniciar_recebimento(self, nome: str) -> RecebimentoDeArquivo: ...

    def localizar(self, referencia: str) -> Path: ...

    def remover(self, referencia: str) -> None: ...


class ImportacaoRepository(Protocol):
    def criar(self, nova: NovaImportacao, status: StatusDaImportacao) -> Importacao: ...

    def buscar(self, importacao_id: int) -> Importacao | None: ...

    def listar(self, filtro: FiltroDeImportacoes) -> PaginaDeImportacoes: ...

    def salvar(self, importacao: Importacao) -> None: ...

    def atualizar_progresso(
        self, importacao_id: int, status: StatusDaImportacao, progresso: int
    ) -> None: ...

    def mesmo_arquivo(self, hash_do_arquivo: str, importacao_id: int) -> list[Importacao]: ...

    def ultima_concluida(self) -> Importacao | None: ...

    def em_andamento(self) -> list[Importacao]: ...


class CarregadorDeDemandas(Protocol):
    def comparar_com_a_base(self, assinaturas: Iterable[tuple[int, int]]) -> ComparacaoComABase: ...

    def carregar(
        self, importacao_id: int, registros: Iterable[RegistroDeDemanda], plano: PlanoDeCarga
    ) -> ResultadoDaCarga: ...

    def desfazer(self, importacao_id: int) -> None: ...

    def listar_registros(
        self, importacao_id: int, limite: int, deslocamento: int
    ) -> PaginaDeRegistros: ...


class AtualizadorDoPainel(Protocol):
    def atualizar(self, ao_avancar: Callable[[int], None]) -> None: ...


class ReferenciasRepository(Protocol):
    def carregar(self) -> Referencias: ...


class FilaDeImportacoes(Protocol):
    def enfileirar(self, tarefa: Callable[[], None]) -> None: ...


class ContribuicoesDaImportacao(Protocol):
    def relatos_guardados(self) -> list[RelatoGuardado]: ...

    def ids_do_pacote(self, importacao_id: int) -> list[UUID]: ...

    def registros_no_mesmo_local(self, ids_locais: list[str]) -> list[RegistroNoMesmoLocal]: ...


class ConferenciaEntreCanais(Protocol):
    def conferir(self, registro: RegistroDeDemanda, endereco: EnderecoDaLinha | None) -> None: ...

    def concluir(self) -> ResultadoDaConferencia: ...


class OrigemPorEndereco(Protocol):
    @property
    def hosts_permitidos(self) -> list[str]: ...

    def baixar(self, endereco: str) -> ArquivoRecebido: ...


class OrigemPorBanco(Protocol):
    def conexoes(self) -> list[str]: ...

    def extrair(self, conexao: str, consulta: str) -> ArquivoRecebido: ...


@dataclass(frozen=True)
class OrigensDeDados:
    por_endereco: OrigemPorEndereco
    por_banco: OrigemPorBanco
