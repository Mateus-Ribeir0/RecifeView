from datetime import date

from pydantic import BaseModel

from app.application.casos_de_uso.encaminhamentos.desempenho import (
    DesempenhoDoOrgao,
    DesempenhoDosOrgaos,
)
from app.domain.encaminhamento.desempenho import IndicadoresDoOrgao, SemanaDoCiclo
from app.domain.encaminhamento.encaminhamento import CanalDeEnvio, Encaminhamento
from app.domain.encaminhamento.orgaos import Orgao, nome_do_orgao


class IndicadoresDoOrgaoResposta(BaseModel):
    orgao: Orgao
    nome_do_orgao: str
    encaminhados: int
    falhas: int
    abertas: int
    novas: int
    em_atendimento: int
    vencidas: int
    resolvidas: int
    resolvidas_no_prazo: int
    pct_no_prazo: float | None
    resolvidas_em_30_dias: int
    devolvidas: int
    mediana_de_dias_ate_resolver: float | None
    voltaram_a_ser_pedidas: int

    @classmethod
    def de_indicadores(cls, item: IndicadoresDoOrgao) -> "IndicadoresDoOrgaoResposta":
        return cls(
            orgao=item.orgao,
            nome_do_orgao=nome_do_orgao(item.orgao),
            encaminhados=item.encaminhados,
            falhas=item.falhas,
            abertas=item.abertas,
            novas=item.novas,
            em_atendimento=item.em_atendimento,
            vencidas=item.vencidas,
            resolvidas=item.resolvidas,
            resolvidas_no_prazo=item.resolvidas_no_prazo,
            pct_no_prazo=item.pct_no_prazo,
            resolvidas_em_30_dias=item.resolvidas_em_30_dias,
            devolvidas=item.devolvidas,
            mediana_de_dias_ate_resolver=item.mediana_de_dias_ate_resolver,
            voltaram_a_ser_pedidas=item.voltaram_a_ser_pedidas,
        )


class SemanaResposta(BaseModel):
    inicio: date
    recebidas: int
    resolvidas: int

    @classmethod
    def de_semana(cls, semana: SemanaDoCiclo) -> "SemanaResposta":
        return cls(inicio=semana.inicio, recebidas=semana.recebidas, resolvidas=semana.resolvidas)


class GrupoDoMesmoProblemaResposta(BaseModel):
    bairro_oficial: str | None
    categoria: str | None
    servico: str | None
    ids: list[int]
    codigos: list[str]
    orgaos: list[str]

    @classmethod
    def de_grupo(cls, grupo: list[Encaminhamento]) -> "GrupoDoMesmoProblemaResposta":
        primeiro = grupo[0].ocorrencia
        return cls(
            bairro_oficial=primeiro.bairro_oficial,
            categoria=primeiro.categoria,
            servico=primeiro.servico,
            ids=[item.id for item in grupo],
            codigos=[item.codigo for item in grupo],
            orgaos=sorted({nome_do_orgao(item.orgao) for item in grupo}),
        )


class DesempenhoDoOrgaoResposta(IndicadoresDoOrgaoResposta):
    canal: CanalDeEnvio
    acessos_ativos: int

    @classmethod
    def de_desempenho(cls, item: DesempenhoDoOrgao) -> "DesempenhoDoOrgaoResposta":
        base = IndicadoresDoOrgaoResposta.de_indicadores(item.indicadores)
        return cls(**base.model_dump(), canal=item.canal, acessos_ativos=item.acessos_ativos)


class DesempenhoResposta(BaseModel):
    hoje: date
    orgaos: list[DesempenhoDoOrgaoResposta]
    semanas: list[SemanaResposta]
    grupos_do_mesmo_problema: list[GrupoDoMesmoProblemaResposta]

    @classmethod
    def de_desempenho(cls, desempenho: DesempenhoDosOrgaos) -> "DesempenhoResposta":
        return cls(
            hoje=desempenho.hoje,
            orgaos=[DesempenhoDoOrgaoResposta.de_desempenho(item) for item in desempenho.orgaos],
            semanas=[SemanaResposta.de_semana(item) for item in desempenho.semanas],
            grupos_do_mesmo_problema=[
                GrupoDoMesmoProblemaResposta.de_grupo(grupo)
                for grupo in desempenho.grupos_do_mesmo_problema
            ],
        )
