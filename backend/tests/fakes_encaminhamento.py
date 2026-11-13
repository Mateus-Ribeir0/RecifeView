from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from uuid import UUID

from app.application.casos_de_uso.encaminhamentos.avisos import AvisosDoCiclo
from app.application.casos_de_uso.encaminhamentos.servicos import ServicosDeEncaminhamento
from app.application.portas.encaminhamentos import (
    EnvioAoOrgaoFalhou,
    FiltroDeEncaminhamentos,
    MudancaDeSituacao,
    NovoEncaminhamento,
    PaginaDeEncaminhamentos,
    PendenciasDosEncaminhamentos,
    ResumoDosEncaminhamentos,
    TokenDeRetorno,
)
from app.domain.ahp import IndicadoresDoBairro
from app.domain.encaminhamento.avisos import Aviso
from app.domain.encaminhamento.encaminhamento import (
    AutorDoEvento,
    CanalDeEnvio,
    Encaminhamento,
    EventoDoEncaminhamento,
    OcorrenciaEncaminhavel,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.mensagem import MensagemAoOrgao
from app.domain.encaminhamento.orgaos import Orgao
from app.domain.encaminhamento.sugestao import CitacoesDoTema
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.prioridade import FonteDaFila, Ocorrencia
from tests.fakes import RelogioFixo

ENDERECO_DO_SITE = "https://recifeview.exemplo"


def ocorrencia_de_teste(chave: int = 1, **alteracoes: object) -> OcorrenciaEncaminhavel:
    valores: dict[str, object] = {
        "chave_registro": chave,
        "fonte": Fonte.CENTRAL_156.value,
        "data_abertura": date(2026, 9, 1),
        "categoria": "DRENAGEM",
        "servico": "LIMPEZA DE GALERIAS E VALETAS",
        "bairro_oficial": "AFOGADOS",
        "rpa": "5",
        "situacao": "ABERTA",
        "orgao": "EMLURB",
        "protocolo": None,
    }
    return OcorrenciaEncaminhavel(**(valores | alteracoes))  # type: ignore[arg-type]


@dataclass
class Guardado:
    encaminhamento: Encaminhamento
    token: TokenDeRetorno


class EncaminhamentosEmMemoria:
    def __init__(self, *ocorrencias: OcorrenciaEncaminhavel) -> None:
        self.ocorrencias = {ocorrencia.chave_registro: ocorrencia for ocorrencia in ocorrencias}
        self.citacoes: dict[str, CitacoesDoTema] = {}
        self.guardados: dict[int, Guardado] = {}
        self.locais_dos_relatos: dict[UUID, str] = {}

    def ocorrencia(self, chave_registro: int) -> OcorrenciaEncaminhavel | None:
        return self.ocorrencias.get(chave_registro)

    def citacoes_do_tema(self, tema: str) -> CitacoesDoTema:
        return self.citacoes.get(tema, CitacoesDoTema(tema))

    def da_ocorrencia(self, chave_registro: int) -> list[Encaminhamento]:
        return [
            guardado.encaminhamento
            for guardado in self.guardados.values()
            if guardado.encaminhamento.ocorrencia.chave_registro == chave_registro
        ]

    def criar(self, novo: NovoEncaminhamento) -> Encaminhamento:
        encaminhamento_id = len(self.guardados) + 1
        autor = AutorDoEvento.SISTEMA if novo.automatico else AutorDoEvento.GESTAO
        encaminhamento = Encaminhamento(
            id=encaminhamento_id,
            ocorrencia=novo.ocorrencia,
            orgao=novo.orgao,
            orgao_sugerido=novo.orgao_sugerido,
            canal=novo.canal,
            situacao=SituacaoDoEncaminhamento.ENVIADO,
            criado_em=novo.criado_em,
            prazo_de_resposta=novo.prazo_de_resposta,
            atualizado_em=novo.criado_em,
            nota=novo.nota,
            justificativa=novo.justificativa,
            automatico=novo.automatico,
            contribuicao_id=novo.contribuicao_id,
            eventos=(
                EventoDoEncaminhamento(SituacaoDoEncaminhamento.ENVIADO, autor, novo.criado_em),
            ),
        )
        self.guardados[encaminhamento_id] = Guardado(encaminhamento, novo.token)
        return encaminhamento

    def buscar(self, encaminhamento_id: int) -> Encaminhamento | None:
        guardado = self.guardados.get(encaminhamento_id)
        return guardado.encaminhamento if guardado else None

    def buscar_pelo_token(self, hash_do_token: str, agora: datetime) -> Encaminhamento | None:
        for guardado in self.guardados.values():
            if guardado.token.hash == hash_do_token and guardado.token.expira_em > agora:
                return guardado.encaminhamento
        return None

    def mudar_situacao(self, encaminhamento_id: int, mudanca: MudancaDeSituacao) -> None:
        guardado = self.guardados[encaminhamento_id]
        atual = guardado.encaminhamento
        evento = EventoDoEncaminhamento(
            mudanca.situacao,
            mudanca.autor,
            mudanca.ocorrido_em,
            mudanca.observacao,
            mudanca.protocolo_do_orgao,
        )
        guardado.encaminhamento = replace(
            atual,
            situacao=mudanca.situacao,
            atualizado_em=mudanca.ocorrido_em,
            protocolo_do_orgao=mudanca.protocolo_do_orgao or atual.protocolo_do_orgao,
            eventos=(*atual.eventos, evento),
        )

    def preparar_reenvio(
        self, encaminhamento_id: int, token: TokenDeRetorno, canal: CanalDeEnvio
    ) -> None:
        guardado = self.guardados[encaminhamento_id]
        guardado.token = token
        guardado.encaminhamento = replace(guardado.encaminhamento, canal=canal)

    def listar(self, filtro: FiltroDeEncaminhamentos, hoje: date) -> PaginaDeEncaminhamentos:
        itens = [guardado.encaminhamento for guardado in self.guardados.values()]
        return PaginaDeEncaminhamentos(itens, len(itens))

    def resumir(self, hoje: date) -> ResumoDosEncaminhamentos:
        return ResumoDosEncaminhamentos(total=len(self.guardados))

    def contar_pendencias(self, hoje: date) -> PendenciasDosEncaminhamentos:
        ultimos = list(self.ultimos_por_chave(list(self.ocorrencias)).values())
        return PendenciasDosEncaminhamentos(
            devolvidos=sum(1 for item in ultimos if item.situacao.value == "devolvido"),
            falhas=sum(1 for item in ultimos if item.situacao.value == "falhou"),
            prazo_vencido=sum(1 for item in ultimos if item.esta_atrasado(hoje)),
        )

    def local_aproximado_do_relato(self, contribuicao_id: UUID) -> str | None:
        return self.locais_dos_relatos.get(contribuicao_id)

    def vencidos_sem_lembrete(self, hoje: date) -> list[Encaminhamento]:
        return [
            guardado.encaminhamento
            for guardado in self.guardados.values()
            if guardado.encaminhamento.esta_atrasado(hoje)
            and guardado.encaminhamento.lembrete_enviado_em is None
        ]

    def registrar_lembrete(
        self, encaminhamento_id: int, token: TokenDeRetorno, agora: datetime
    ) -> None:
        guardado = self.guardados[encaminhamento_id]
        guardado.token = token
        guardado.encaminhamento = replace(guardado.encaminhamento, lembrete_enviado_em=agora)

    def ultimos_por_relato(self, ids: Sequence[UUID]) -> dict[UUID, Encaminhamento]:
        encaminhados = (guardado.encaminhamento for guardado in self.guardados.values())
        return {
            item.contribuicao_id: item
            for item in encaminhados
            if item.contribuicao_id is not None and item.contribuicao_id in ids
        }

    def ultimos_por_chave(self, chaves: Sequence[int]) -> dict[int, Encaminhamento]:
        return {
            guardado.encaminhamento.ocorrencia.chave_registro: guardado.encaminhamento
            for guardado in self.guardados.values()
            if guardado.encaminhamento.ocorrencia.chave_registro in chaves
        }


@dataclass
class DespachoEmMemoria:
    canais: dict[Orgao, CanalDeEnvio] = field(default_factory=dict)
    enviadas: list[MensagemAoOrgao] = field(default_factory=list)
    falhar: bool = False

    def canal_de(self, orgao: Orgao) -> CanalDeEnvio:
        return self.canais.get(orgao, CanalDeEnvio.LOCAL)

    def enviar(self, mensagem: MensagemAoOrgao) -> None:
        if self.falhar:
            raise EnvioAoOrgaoFalhou
        self.enviadas.append(mensagem)

    def ultimo_token(self) -> str:
        link = str(self.enviadas[-1].dados["link_de_retorno"])
        return link.rsplit("/", 1)[-1]


@dataclass
class PrioridadeFalsa:
    """Fila mínima: um bairro no índice e as ocorrências dadas, todas do 156."""

    ocorrencias: list[Ocorrencia] = field(default_factory=list)

    def indicadores_dos_bairros(self) -> list[IndicadoresDoBairro]:
        return [
            IndicadoresDoBairro("AFOGADOS", "Afogados", "5", 30.0, 28.9, 40.0, 50.0),
            IndicadoresDoBairro("BOA VIAGEM", "Boa Viagem", "6", 1.0, 7.9, 10.0, 20.0),
        ]

    def ocorrencias_156(self, filtros: Filtros) -> list[Ocorrencia]:
        return self.ocorrencias

    def ocorrencias_da_camara(self, filtros: Filtros) -> list[Ocorrencia]:
        return []

    def ocorrencias_da_ouvidoria(self) -> list[Ocorrencia]:
        return []

    def registros_na_base(self, fonte: FonteDaFila) -> int:
        return len(self.ocorrencias)


@dataclass
class DestinatariosEmMemoria:
    quem_encaminhou: str | None = None
    quem_acompanha: list[str] = field(default_factory=list)

    def email_de_quem_encaminhou(self, encaminhamento_id: int) -> str | None:
        return self.quem_encaminhou

    def emails_de_quem_acompanha(self, encaminhamento: Encaminhamento) -> list[str]:
        return list(self.quem_acompanha)


@dataclass
class EntregaEmMemoria:
    entregues: list[tuple[str, Aviso]] = field(default_factory=list)

    def entregar(self, para: str, aviso: Aviso) -> None:
        self.entregues.append((para, aviso))

    def para(self, email: str) -> list[Aviso]:
        return [aviso for destino, aviso in self.entregues if destino == email]


@dataclass
class Ambiente:
    """As portas falsas juntas, para o teste conferir o que cada parte recebeu."""

    repositorio: EncaminhamentosEmMemoria
    despacho: DespachoEmMemoria = field(default_factory=DespachoEmMemoria)
    relogio: RelogioFixo = field(default_factory=RelogioFixo)
    destinatarios: DestinatariosEmMemoria = field(default_factory=DestinatariosEmMemoria)
    entrega: EntregaEmMemoria = field(default_factory=EntregaEmMemoria)

    def servicos(self) -> ServicosDeEncaminhamento:
        avisos = AvisosDoCiclo(self.destinatarios, self.entrega, ENDERECO_DO_SITE)
        return ServicosDeEncaminhamento(self.repositorio, self.despacho, self.relogio, avisos)


def criar_servicos_de_encaminhamento(
    repositorio: EncaminhamentosEmMemoria,
    despacho: DespachoEmMemoria | None = None,
    relogio: RelogioFixo | None = None,
) -> ServicosDeEncaminhamento:
    return Ambiente(
        repositorio, despacho or DespachoEmMemoria(), relogio or RelogioFixo()
    ).servicos()
