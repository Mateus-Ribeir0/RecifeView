from datetime import date, datetime

from pydantic import BaseModel, Field

from app.api.schemas.desempenho import (
    GrupoDoMesmoProblemaResposta,
    IndicadoresDoOrgaoResposta,
    SemanaResposta,
)
from app.api.schemas.encaminhamentos import MesmoProblemaResposta, RespostaDoOrgaoEntrada
from app.application.casos_de_uso.corporativo.ocorrencias import (
    AbaDoOrgao,
    FilaDoOrgao,
    ItemDaFila,
    OcorrenciaDoOrgao,
)
from app.application.casos_de_uso.corporativo.painel import PainelDoOrgao
from app.application.casos_de_uso.corporativo.resposta import MAXIMO_DE_OCORRENCIAS_JUNTAS
from app.domain.demanda_do_orgao import DemandaDoOrgao, PeriodoEmAnos
from app.domain.encaminhamento.encaminhamento import (
    SITUACOES_DE_RETORNO,
    TRANSICOES_PERMITIDAS,
    AutorDoEvento,
    Encaminhamento,
    EventoDoEncaminhamento,
    SituacaoDoEncaminhamento,
)
from app.domain.encaminhamento.orgaos import Orgao, nome_do_orgao, nomes_na_fonte


class OcorrenciaNaFilaResposta(BaseModel):
    """Sem o protocolo do cidadão: ele só aparece no detalhe, como na mensagem ao órgão."""

    id: int
    codigo: str
    fonte: str
    categoria: str | None
    servico: str | None
    bairro_oficial: str | None
    rpa: str | None
    local_aproximado: str | None
    data_abertura: date | None
    situacao: SituacaoDoEncaminhamento
    atrasado: bool
    criado_em: datetime
    prazo_de_resposta: date
    dias_para_o_prazo: int
    previsao: date | None
    resposta_ao_cidadao: str | None
    mesmo_problema_no_orgao: int = 0
    mesmo_problema_em_outros_orgaos: int = 0
    pessoas_que_acompanham: int = 0

    @classmethod
    def de_encaminhamento(cls, item: Encaminhamento, hoje: date) -> "OcorrenciaNaFilaResposta":
        ocorrencia = item.ocorrencia
        return cls(
            id=item.id,
            codigo=item.codigo,
            fonte=ocorrencia.fonte,
            categoria=ocorrencia.categoria,
            servico=ocorrencia.servico,
            bairro_oficial=ocorrencia.bairro_oficial,
            rpa=ocorrencia.rpa,
            local_aproximado=ocorrencia.referencia_de_local,
            data_abertura=ocorrencia.data_abertura,
            situacao=item.situacao,
            atrasado=item.esta_atrasado(hoje),
            criado_em=item.criado_em,
            prazo_de_resposta=item.prazo_de_resposta,
            dias_para_o_prazo=item.dias_para_o_prazo(hoje),
            previsao=item.previsao,
            resposta_ao_cidadao=item.resposta_ao_cidadao,
        )

    @classmethod
    def de_item(cls, item: ItemDaFila, hoje: date) -> "OcorrenciaNaFilaResposta":
        base = cls.de_encaminhamento(item.encaminhamento, hoje)
        return base.model_copy(
            update={
                "mesmo_problema_no_orgao": item.mesmo_problema_no_orgao,
                "mesmo_problema_em_outros_orgaos": item.mesmo_problema_em_outros_orgaos,
                "pessoas_que_acompanham": item.pessoas_que_acompanham,
            }
        )


class FilaDoOrgaoResposta(BaseModel):
    hoje: date
    itens: list[OcorrenciaNaFilaResposta]
    total: int
    por_aba: dict[AbaDoOrgao, int]
    bairros: list[str]
    categorias: list[str]

    @classmethod
    def de_fila(cls, fila: FilaDoOrgao, hoje: date) -> "FilaDoOrgaoResposta":
        return cls(
            hoje=hoje,
            itens=[OcorrenciaNaFilaResposta.de_item(item, hoje) for item in fila.itens],
            total=fila.total,
            por_aba=fila.por_aba,
            bairros=fila.opcoes.bairros,
            categorias=fila.opcoes.categorias,
        )


class EventoDoOrgaoResposta(BaseModel):
    situacao: SituacaoDoEncaminhamento
    autor: AutorDoEvento
    ocorrido_em: datetime
    observacao: str | None
    resposta_ao_cidadao: str | None
    previsao: date | None
    protocolo_do_orgao: str | None

    @classmethod
    def de_evento(cls, evento: EventoDoEncaminhamento) -> "EventoDoOrgaoResposta":
        return cls(
            situacao=evento.situacao,
            autor=evento.autor,
            ocorrido_em=evento.ocorrido_em,
            observacao=evento.observacao,
            resposta_ao_cidadao=evento.resposta_ao_cidadao,
            previsao=evento.previsao,
            protocolo_do_orgao=evento.protocolo_do_orgao,
        )


class OcorrenciaDoOrgaoResposta(OcorrenciaNaFilaResposta):
    protocolo_de_origem: str | None
    situacao_na_fonte: str | None
    justificativa: str | None
    nota: float | None
    protocolo_do_orgao: str | None
    registros_do_mesmo_local: int
    pode_responder: bool
    respostas_possiveis: list[SituacaoDoEncaminhamento]
    mesmo_problema: list[MesmoProblemaResposta]
    eventos: list[EventoDoOrgaoResposta]

    @classmethod
    def de_ocorrencia(
        cls, detalhe: OcorrenciaDoOrgao, orgao: Orgao, hoje: date
    ) -> "OcorrenciaDoOrgaoResposta":
        item = detalhe.encaminhamento
        no_orgao = sum(
            1 for parecido in detalhe.mesmo_problema if parecido.encaminhamento.orgao is orgao
        )
        base = OcorrenciaNaFilaResposta.de_encaminhamento(item, hoje)
        possiveis = TRANSICOES_PERMITIDAS[item.situacao]
        return cls(
            **base.model_dump(
                exclude={
                    "mesmo_problema_no_orgao",
                    "mesmo_problema_em_outros_orgaos",
                    "pessoas_que_acompanham",
                }
            ),
            mesmo_problema_no_orgao=no_orgao,
            mesmo_problema_em_outros_orgaos=len(detalhe.mesmo_problema) - no_orgao,
            pessoas_que_acompanham=detalhe.pessoas_que_acompanham,
            protocolo_de_origem=item.ocorrencia.protocolo,
            situacao_na_fonte=item.ocorrencia.situacao,
            justificativa=item.justificativa,
            nota=item.nota,
            protocolo_do_orgao=item.protocolo_do_orgao,
            registros_do_mesmo_local=detalhe.registros_do_mesmo_local,
            pode_responder=detalhe.pode_responder,
            respostas_possiveis=[
                situacao for situacao in SITUACOES_DE_RETORNO if situacao in possiveis
            ],
            mesmo_problema=[
                MesmoProblemaResposta.de_item(parecido, hoje, orgao)
                for parecido in detalhe.mesmo_problema
            ],
            eventos=[EventoDoOrgaoResposta.de_evento(evento) for evento in item.eventos],
        )


class RespostaComoOrgaoEntrada(RespostaDoOrgaoEntrada):
    tambem: list[int] = Field(default_factory=list, max_length=MAXIMO_DE_OCORRENCIAS_JUNTAS)


class RespostaRegistradaResposta(BaseModel):
    codigo: str
    situacao: SituacaoDoEncaminhamento
    codigos_juntos: list[str]


class ContagemResposta(BaseModel):
    rotulo: str
    quantidade: int


class PainelDoOrgaoResposta(BaseModel):
    hoje: date
    orgao: Orgao
    nome_do_orgao: str
    indicadores: IndicadoresDoOrgaoResposta
    semanas: list[SemanaResposta]
    abertas_por_bairro: list[ContagemResposta]
    resolvidas_por_tema: list[ContagemResposta]
    mais_urgentes: list[OcorrenciaNaFilaResposta]
    grupos_do_mesmo_problema: list[GrupoDoMesmoProblemaResposta]
    pessoas_com_retorno: int

    @classmethod
    def de_painel(cls, painel: PainelDoOrgao, orgao: Orgao) -> "PainelDoOrgaoResposta":
        return cls(
            hoje=painel.hoje,
            orgao=orgao,
            nome_do_orgao=nome_do_orgao(orgao),
            indicadores=IndicadoresDoOrgaoResposta.de_indicadores(painel.indicadores),
            semanas=[SemanaResposta.de_semana(semana) for semana in painel.semanas],
            abertas_por_bairro=[
                ContagemResposta(rotulo=bairro, quantidade=quantidade)
                for bairro, quantidade in sorted(painel.abertas_por_bairro.items())
            ],
            resolvidas_por_tema=[
                ContagemResposta(rotulo=item.categoria, quantidade=item.quantidade)
                for item in painel.resolvidas_por_tema
            ],
            mais_urgentes=[
                OcorrenciaNaFilaResposta.de_encaminhamento(item, painel.hoje)
                for item in painel.mais_urgentes
            ],
            grupos_do_mesmo_problema=[
                GrupoDoMesmoProblemaResposta.de_grupo(grupo)
                for grupo in painel.grupos_do_mesmo_problema
            ],
            pessoas_com_retorno=painel.pessoas_com_retorno,
        )


class DemandaPorAnoResposta(BaseModel):
    ano: int
    fonte: str
    quantidade: int


class DemandaDoOrgaoResposta(BaseModel):
    orgao: Orgao
    nome_do_orgao: str
    ano_inicio: int
    ano_fim: int
    nomes_na_fonte: list[str]
    total: int
    sem_bairro: int
    por_ano: list[DemandaPorAnoResposta]
    por_bairro: list[ContagemResposta]
    por_tema: list[ContagemResposta]
    por_situacao: list[ContagemResposta]

    @classmethod
    def de_demanda(
        cls, demanda: DemandaDoOrgao, orgao: Orgao, periodo: PeriodoEmAnos
    ) -> "DemandaDoOrgaoResposta":
        return cls(
            orgao=orgao,
            nome_do_orgao=nome_do_orgao(orgao),
            ano_inicio=periodo.ano_inicio,
            ano_fim=periodo.ano_fim,
            nomes_na_fonte=nomes_na_fonte(orgao),
            total=demanda.total,
            sem_bairro=demanda.sem_bairro,
            por_ano=[
                DemandaPorAnoResposta(ano=item.ano, fonte=item.fonte, quantidade=item.quantidade)
                for item in demanda.por_ano
            ],
            por_bairro=[
                ContagemResposta(rotulo=bairro, quantidade=quantidade)
                for bairro, quantidade in sorted(demanda.por_bairro.items())
            ],
            por_tema=[
                ContagemResposta(rotulo=item.rotulo, quantidade=item.quantidade)
                for item in demanda.por_tema
            ],
            por_situacao=[
                ContagemResposta(rotulo=item.rotulo, quantidade=item.quantidade)
                for item in demanda.por_situacao
            ],
        )
