from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from pathlib import Path
from uuid import UUID

from app.application.casos_de_uso.contribuicoes.servicos import ServicosDeContribuicoes
from app.application.casos_de_uso.importacoes.servicos import ServicosDeImportacao
from app.application.portas.contribuicoes import (
    BairroDoFormulario,
    DecisaoRegistrada,
    FiltroDaCidade,
    OcorrenciaDaCidade,
    OcorrenciaDoPacote,
    PaginaDeOcorrencias,
    ParNovo,
    ParParaRevisar,
    ResumoDasContribuicoes,
)
from app.application.portas.importacoes import (
    ArquivoRecebido,
    ComparacaoComABase,
    FiltroDeImportacoes,
    NovaImportacao,
    PaginaDeImportacoes,
    PaginaDeRegistros,
    PlanoDeCarga,
    RegistroNoMesmoLocal,
    ResultadoDaCarga,
)
from app.domain.contribuicao.conferencia import RelatoGuardado
from app.domain.contribuicao.contribuicao import Contribuicao, DecisaoDoPar
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
    ultimo_plano: PlanoDeCarga | None = None

    def comparar_com_a_base(self, assinaturas: Iterable[tuple[int, int]]) -> ComparacaoComABase:
        list(assinaturas)
        return self.comparacao

    def carregar(
        self, importacao_id: int, registros: Iterable[RegistroDeDemanda], plano: PlanoDeCarga
    ) -> ResultadoDaCarga:
        self.carregados = list(registros)
        self.ultimo_plano = plano
        return ResultadoDaCarga(novas=len(self.carregados), retiradas=len(plano.retirada.ids))

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


@dataclass
class ContribuicoesEmMemoria:
    itens: list[Contribuicao] = field(default_factory=list)
    pares: list[ParNovo] = field(default_factory=list)
    decisoes: dict[int, DecisaoDoPar] = field(default_factory=dict)
    relatos: list[RelatoGuardado] = field(default_factory=list)
    prontas: list[OcorrenciaDoPacote] = field(default_factory=list)
    no_pacote: list[UUID] = field(default_factory=list)
    na_base: list[RegistroNoMesmoLocal] = field(default_factory=list)
    limites_de_expurgo: list[datetime] = field(default_factory=list)
    da_cidade: list[OcorrenciaDaCidade] = field(default_factory=list)
    filtros_da_cidade: list[FiltroDaCidade] = field(default_factory=list)

    def ocorrencias_da_cidade(self, filtro: FiltroDaCidade) -> list[OcorrenciaDaCidade]:
        self.filtros_da_cidade.append(filtro)
        return self.da_cidade

    def buscar_por_chave_de_envio(self, chave: str) -> Contribuicao | None:
        return next((item for item in self.itens if item.chave_de_envio == chave), None)

    def candidatas(self, bairro: str, categoria: str, desde: date) -> list[Contribuicao]:
        return [
            item
            for item in self.itens
            if item.bairro_oficial == bairro
            and item.categoria == categoria
            and item.data_relato >= desde
            and item.principal_id is None
        ]

    def inserir(self, contribuicao: Contribuicao, pares: Sequence[ParNovo]) -> Contribuicao:
        self.itens.append(contribuicao)
        self.pares.extend(pares)
        return contribuicao

    def resumir(self) -> ResumoDasContribuicoes:
        return ResumoDasContribuicoes(relatos=len(self.itens))

    def listar_ocorrencias(self, limite: int, deslocamento: int) -> PaginaDeOcorrencias:
        return PaginaDeOcorrencias([], 0)

    def listar_pares_abertos(self, limite: int) -> list[ParParaRevisar]:
        return []

    def decidir_par(self, par_id: int, decisao: DecisaoRegistrada) -> bool:
        if par_id in self.decisoes or par_id >= len(self.pares):
            return False
        self.decisoes[par_id] = decisao.decisao
        return True

    def contar_pares_abertos(self) -> int:
        return len(self.pares) - len(self.decisoes)

    def prontas_para_pacote(self) -> list[OcorrenciaDoPacote]:
        return self.prontas

    def marcar_no_pacote(self, ids: Sequence[UUID], importacao_id: int) -> None:
        self.no_pacote.extend(ids)

    def expurgar_enderecos(self, recebidas_ate: datetime, agora: datetime) -> int:
        self.limites_de_expurgo.append(recebidas_ate)
        return 0

    def relatos_guardados(self) -> list[RelatoGuardado]:
        return self.relatos

    def ids_do_pacote(self, importacao_id: int) -> list[UUID]:
        return self.no_pacote

    def registros_no_mesmo_local(self, ids_locais: list[str]) -> list[RegistroNoMesmoLocal]:
        return [item for item in self.na_base if item.id_local in ids_locais]


@dataclass
class ReferenciaFalsa:
    vias: dict[str, list[str]] = field(default_factory=dict)
    somadas: list[tuple[str, str, int]] = field(default_factory=list)

    def bairros(self) -> list[BairroDoFormulario]:
        return [BairroDoFormulario("AFOGADOS", "Afogados", "5")]

    def logradouros(self, bairro: str) -> list[str]:
        return self.vias.get(bairro, [])

    def somar_logradouros(self, vias: Iterable[tuple[str, str, int]]) -> int:
        self.somadas = list(vias)
        return len(self.somadas)


@dataclass
class LimiteFalso:
    aberto: bool = True

    def permitir(self, origem: str) -> bool:
        return self.aberto


def criar_servicos_de_contribuicoes(
    importacao: ServicosDeImportacao, sal: str | None = None
) -> ServicosDeContribuicoes:
    contribuicoes = importacao.contribuicoes
    assert isinstance(contribuicoes, ContribuicoesEmMemoria)
    return ServicosDeContribuicoes(
        contribuicoes=contribuicoes,
        referencia=ReferenciaFalsa({"AFOGADOS": ["RUA DA ESPERANCA FICTICIA"]}),
        limite=LimiteFalso(),
        relogio=RelogioFixo(),
        importacao=importacao,
        sal=sal,
    )


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
        contribuicoes=ContribuicoesEmMemoria(),
    )
