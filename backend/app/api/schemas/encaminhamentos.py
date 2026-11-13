from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.api.schemas.comum import ChaveDoRegistro
from app.api.schemas.painel import Esquema
from app.application.casos_de_uso.encaminhamentos.consultar import QuadroDeEncaminhamentos
from app.application.casos_de_uso.encaminhamentos.encaminhar import OcorrenciaParaEncaminhar
from app.domain.ahp import NOTA_MAXIMA
from app.domain.encaminhamento.encaminhamento import (
    SITUACOES_DE_RETORNO,
    TAMANHO_MAXIMO_DA_OBSERVACAO,
    TAMANHO_MAXIMO_DO_PROTOCOLO_DO_ORGAO,
    TRANSICOES_PERMITIDAS,
    AutorDoEvento,
    CanalDeEnvio,
    Encaminhamento,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.orgaos import CATALOGO_DE_ORGAOS, Orgao, nome_do_orgao
from app.domain.encaminhamento.sugestao import MotivoDaSugestao, SugestaoDeDestino

TAMANHO_MAXIMO_DO_TOKEN = 100


class OrgaoResposta(BaseModel):
    orgao: Orgao
    nome: str
    fora_da_prefeitura: bool
    canal: CanalDeEnvio


class OcorrenciaEncaminhavelResposta(Esquema):
    chave_registro: ChaveDoRegistro
    fonte: str
    data_abertura: date | None
    categoria: str | None
    servico: str | None
    bairro_oficial: str | None
    rpa: str | None
    situacao: str | None
    orgao: str | None
    protocolo: str | None
    referencia_de_local: str | None


class EventoResposta(Esquema):
    situacao: SituacaoDoEncaminhamento
    autor: AutorDoEvento
    ocorrido_em: datetime
    observacao: str | None
    protocolo_do_orgao: str | None


class EncaminhamentoResposta(BaseModel):
    id: int
    codigo: str
    ocorrencia: OcorrenciaEncaminhavelResposta
    orgao: Orgao
    nome_do_orgao: str
    orgao_sugerido: Orgao | None
    nome_do_orgao_sugerido: str | None
    canal: CanalDeEnvio
    situacao: SituacaoDoEncaminhamento
    atrasado: bool
    criado_em: datetime
    prazo_de_resposta: date
    atualizado_em: datetime
    nota: float | None
    justificativa: str | None
    automatico: bool
    protocolo_do_orgao: str | None
    lembrete_enviado_em: datetime | None
    contribuicao_id: UUID | None
    eventos: list[EventoResposta]

    @classmethod
    def de_encaminhamento(cls, item: Encaminhamento, hoje: date) -> "EncaminhamentoResposta":
        return cls(
            id=item.id,
            codigo=item.codigo,
            ocorrencia=OcorrenciaEncaminhavelResposta.model_validate(item.ocorrencia),
            orgao=item.orgao,
            nome_do_orgao=nome_do_orgao(item.orgao),
            orgao_sugerido=item.orgao_sugerido,
            nome_do_orgao_sugerido=(
                nome_do_orgao(item.orgao_sugerido) if item.orgao_sugerido else None
            ),
            canal=item.canal,
            situacao=item.situacao,
            atrasado=item.esta_atrasado(hoje),
            criado_em=item.criado_em,
            prazo_de_resposta=item.prazo_de_resposta,
            atualizado_em=item.atualizado_em,
            nota=item.nota,
            justificativa=item.justificativa,
            automatico=item.automatico,
            protocolo_do_orgao=item.protocolo_do_orgao,
            lembrete_enviado_em=item.lembrete_enviado_em,
            contribuicao_id=item.contribuicao_id,
            eventos=[EventoResposta.model_validate(evento) for evento in item.eventos],
        )


class ParticipacaoResposta(BaseModel):
    orgao: Orgao
    nome: str
    indicacoes: int
    pct: float


class SugestaoResposta(BaseModel):
    orgao: Orgao | None
    motivo: MotivoDaSugestao
    tema: str | None
    indicacoes_do_tema: int
    participacoes: list[ParticipacaoResposta]

    @classmethod
    def de_sugestao(cls, sugestao: SugestaoDeDestino) -> "SugestaoResposta":
        return cls(
            orgao=sugestao.orgao,
            motivo=sugestao.motivo,
            tema=sugestao.tema,
            indicacoes_do_tema=sugestao.indicacoes_do_tema,
            participacoes=[
                ParticipacaoResposta(
                    orgao=item.orgao,
                    nome=nome_do_orgao(item.orgao),
                    indicacoes=item.indicacoes,
                    pct=item.pct,
                )
                for item in sugestao.participacoes
            ],
        )


def orgaos_com_canal(canais: dict[Orgao, CanalDeEnvio]) -> list[OrgaoResposta]:
    return [
        OrgaoResposta(
            orgao=dados.orgao,
            nome=dados.nome,
            fora_da_prefeitura=dados.fora_da_prefeitura,
            canal=canais.get(dados.orgao, CanalDeEnvio.LOCAL),
        )
        for dados in CATALOGO_DE_ORGAOS
    ]


class PreparoResposta(BaseModel):
    ocorrencia: OcorrenciaEncaminhavelResposta
    sugestao: SugestaoResposta
    orgaos: list[OrgaoResposta]
    encaminhamentos: list[EncaminhamentoResposta]
    pode_encaminhar: bool

    @classmethod
    def de_preparo(cls, preparo: OcorrenciaParaEncaminhar, hoje: date) -> "PreparoResposta":
        return cls(
            ocorrencia=OcorrenciaEncaminhavelResposta.model_validate(preparo.ocorrencia),
            sugestao=SugestaoResposta.de_sugestao(preparo.sugestao),
            orgaos=orgaos_com_canal(preparo.canais),
            encaminhamentos=[
                EncaminhamentoResposta.de_encaminhamento(item, hoje)
                for item in preparo.encaminhamentos
            ],
            pode_encaminhar=preparo.pode_encaminhar,
        )


class EncaminharEntrada(BaseModel):
    chave_registro: ChaveDoRegistro
    orgao: Orgao
    justificativa: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_DA_OBSERVACAO)
    nota: float | None = Field(default=None, ge=0, le=NOTA_MAXIMA)
    contribuicao_id: UUID | None = None


class RespostaDoOrgaoEntrada(BaseModel):
    situacao: SituacaoDoEncaminhamento
    protocolo_do_orgao: str | None = Field(
        default=None, max_length=TAMANHO_MAXIMO_DO_PROTOCOLO_DO_ORGAO
    )
    observacao: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_DA_OBSERVACAO)


class TokenEntrada(BaseModel):
    token: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_DO_TOKEN)


class RetornoPeloLinkEntrada(RespostaDoOrgaoEntrada, TokenEntrada):
    pass


class ResumoResposta(BaseModel):
    total: int
    abertos: int
    atrasados: int
    por_situacao: dict[SituacaoDoEncaminhamento, int]
    mediana_de_dias_ate_resolver: float | None


class QuadroResposta(BaseModel):
    hoje: date
    resumo: ResumoResposta
    itens: list[EncaminhamentoResposta]
    total: int

    @classmethod
    def de_quadro(cls, quadro: QuadroDeEncaminhamentos) -> "QuadroResposta":
        resumo = quadro.resumo
        return cls(
            hoje=quadro.hoje,
            resumo=ResumoResposta(
                total=resumo.total,
                abertos=resumo.abertos,
                atrasados=resumo.atrasados,
                por_situacao=resumo.por_situacao,
                mediana_de_dias_ate_resolver=resumo.mediana_de_dias_ate_resolver,
            ),
            itens=[
                EncaminhamentoResposta.de_encaminhamento(item, quadro.hoje)
                for item in quadro.pagina.itens
            ],
            total=quadro.pagina.total,
        )


class EventoParaOOrgaoResposta(Esquema):
    situacao: SituacaoDoEncaminhamento
    autor: AutorDoEvento
    ocorrido_em: datetime


class EncaminhamentoParaOOrgaoResposta(BaseModel):
    """O que o órgão vê pelo link: a ocorrência e o ciclo, sem o que é interno da gestão."""

    codigo: str
    orgao: Orgao
    nome_do_orgao: str
    ocorrencia: OcorrenciaEncaminhavelResposta
    situacao: SituacaoDoEncaminhamento
    criado_em: datetime
    prazo_de_resposta: date
    justificativa: str | None
    protocolo_do_orgao: str | None
    respostas_possiveis: list[SituacaoDoEncaminhamento]
    eventos: list[EventoParaOOrgaoResposta]

    @classmethod
    def de_encaminhamento(cls, item: Encaminhamento) -> "EncaminhamentoParaOOrgaoResposta":
        possiveis = TRANSICOES_PERMITIDAS[item.situacao]
        return cls(
            codigo=item.codigo,
            orgao=item.orgao,
            nome_do_orgao=nome_do_orgao(item.orgao),
            ocorrencia=OcorrenciaEncaminhavelResposta.model_validate(item.ocorrencia),
            situacao=item.situacao,
            criado_em=item.criado_em,
            prazo_de_resposta=item.prazo_de_resposta,
            justificativa=item.justificativa,
            protocolo_do_orgao=item.protocolo_do_orgao,
            respostas_possiveis=[
                situacao for situacao in SITUACOES_DE_RETORNO if situacao in possiveis
            ],
            eventos=[EventoParaOOrgaoResposta.model_validate(evento) for evento in item.eventos],
        )


class PendenciasResposta(BaseModel):
    devolvidos: int
    falhas: int
    prazo_vencido: int
    pedem_acao: int
    duplas_no_pente_fino: int
