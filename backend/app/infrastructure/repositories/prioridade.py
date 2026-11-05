from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.ahp import IndicadoresDoBairro
from app.domain.filtros import Filtros
from app.domain.fontes import Fonte
from app.domain.prioridade import FonteDaFila, Ocorrencia
from app.infrastructure.repositories.recorte import por_categoria, por_territorio

INDICADORES = """
SELECT
    bairro_oficial, nome, rpa, taxa_defesa_civil, pct_favela, pct_atraso_156, pct_reincidencia_156
FROM ouro.mv_indicadores_bairro
ORDER BY bairro_oficial
"""
TOTAL_DE_REGISTROS = "SELECT registros FROM ouro.mv_referencia_por_fonte WHERE fonte = :fonte"
TOTAL_DE_INDICACOES = "SELECT count(*) FROM ouro.mv_camara_indicacoes"
FONTES_DO_REGISTRO = {
    FonteDaFila.CENTRAL_156: Fonte.CENTRAL_156.value,
    FonteDaFila.OUVIDORIA: Fonte.OUVIDORIA.value,
}


class PrioridadeRepositorySql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def indicadores_dos_bairros(self) -> list[IndicadoresDoBairro]:
        return [IndicadoresDoBairro(*linha) for linha in self._sessao.execute(text(INDICADORES))]

    def ocorrencias_156(self, filtros: Filtros) -> list[Ocorrencia]:
        recorte = (
            por_territorio(filtros).com(por_categoria(filtros)).com_condicao("t.data_fim IS NULL")
        )
        consulta = f"""
        SELECT
            t.data_abertura, r.data_referencia - t.data_abertura, t.prazo_tipico_dias,
            t.pedidos_anteriores, t.bairro_oficial, t.rpa, t.categoria, t.servico, t.situacao
        FROM ouro.mv_linha_do_tempo_156 t
        CROSS JOIN ouro.vw_referencia r
        {recorte.onde}
        """
        linhas = self._sessao.execute(text(consulta), recorte.parametros)
        return [Ocorrencia(*linha) for linha in linhas]

    def ocorrencias_da_camara(self, filtros: Filtros) -> list[Ocorrencia]:
        recorte = (
            por_territorio(filtros)
            .com(por_categoria(filtros))
            .com_condicao("t.data_resposta IS NULL")
        )
        consulta = f"""
        SELECT
            t.data_abertura, r.data_referencia - t.data_envio, t.prazo_tipico_dias,
            t.pedidos_anteriores, t.bairro_oficial, t.rpa, t.categoria, t.orgao, t.canal_envio,
            t.data_envio
        FROM ouro.mv_linha_do_tempo_camara t
        CROSS JOIN ouro.vw_referencia r
        {recorte.onde}
        """
        return [
            Ocorrencia(
                data_abertura=abertura,
                idade_dias=idade,
                prazo_tipico_dias=prazo,
                pedidos_anteriores=anteriores,
                bairro_oficial=bairro,
                rpa=rpa,
                categoria=categoria,
                orgao=orgao,
                canal=canal,
                data_envio=envio,
            )
            for abertura, idade, prazo, anteriores, bairro, rpa, categoria, orgao, canal, envio in (
                self._sessao.execute(text(consulta), recorte.parametros)
            )
        ]

    def ocorrencias_da_ouvidoria(self) -> list[Ocorrencia]:
        consulta = """
        SELECT
            t.data_abertura, t.data_prazo, r.data_referencia - t.data_prazo,
            r.data_referencia - t.data_abertura, t.assunto, t.natureza, t.orgao, t.canal_entrada
        FROM ouro.mv_linha_do_tempo_ouvidoria t
        CROSS JOIN ouro.vw_referencia r
        WHERE t.data_fim IS NULL
        """
        return [
            Ocorrencia(
                data_abertura=abertura,
                idade_dias=idade,
                servico=assunto,
                natureza=natureza,
                orgao=orgao,
                canal=canal,
                data_prazo=prazo,
                dias_alem_do_prazo=alem,
            )
            for abertura, prazo, alem, idade, assunto, natureza, orgao, canal in (
                self._sessao.execute(text(consulta))
            )
        ]

    def registros_na_base(self, fonte: FonteDaFila) -> int:
        if fonte is FonteDaFila.CAMARA:
            return self._sessao.scalar(text(TOTAL_DE_INDICACOES)) or 0
        parametros = {"fonte": FONTES_DO_REGISTRO[fonte]}
        return self._sessao.scalar(text(TOTAL_DE_REGISTROS), parametros) or 0
