from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta

from app.application.portas.painel import PrioridadeRepository, WarRoomRepository
from app.domain.ahp import JULGAMENTOS_PADRAO, calcular_pesos
from app.domain.erros import DiaForaDaJanela
from app.domain.prioridade import (
    NOTA_ALTA,
    Ocorrencia,
    OcorrenciaClassificada,
    classificar_ocorrencias,
)
from app.domain.war_room import (
    CATEGORIAS_COM_MAIS_ATRASO,
    DIAS_DA_JANELA,
    DIAS_SIMULADOS,
    NOTA_MUITO_ALTA,
    PEDIDOS_NA_FILA_DO_DIA,
    AtrasoDoBairro,
    CalendarioDaWarRoom,
    ContagemDeCategoria,
    DiaDaSerie,
    EstoqueDoDia,
    FilaDoDia,
    QuadroDoDia,
)


def _esta_atrasado(ocorrencia: Ocorrencia) -> bool:
    prazo = ocorrencia.prazo_tipico_dias
    return prazo is not None and ocorrencia.idade_dias > prazo


def _atraso_por_bairro(abertos: list[Ocorrencia]) -> list[AtrasoDoBairro]:
    contagem = Counter(
        item.bairro_oficial for item in abertos if _esta_atrasado(item) and item.bairro_oficial
    )
    return [AtrasoDoBairro(str(bairro), n) for bairro, n in contagem.items()]


def _categorias_com_atraso(abertos: list[Ocorrencia]) -> list[ContagemDeCategoria]:
    total: Counter[str] = Counter()
    atrasados: Counter[str] = Counter()
    for item in abertos:
        if item.categoria is None:
            continue
        total[item.categoria] += 1
        atrasados[item.categoria] += _esta_atrasado(item)
    maiores = atrasados.most_common(CATEGORIAS_COM_MAIS_ATRASO)
    return [ContagemDeCategoria(categoria, total[categoria], n) for categoria, n in maiores]


def _item_da_fila(item: OcorrenciaClassificada) -> FilaDoDia:
    ocorrencia = item.ocorrencia
    return FilaDoDia(
        item.indice,
        ocorrencia.servico,
        ocorrencia.bairro_oficial,
        ocorrencia.idade_dias,
        ocorrencia.pedidos_anteriores,
    )


@dataclass(frozen=True)
class ConsultarCalendarioDaWarRoom:
    war_room: WarRoomRepository

    def executar(self) -> CalendarioDaWarRoom:
        return self.war_room.calendario()


@dataclass(frozen=True)
class ConsultarQuadroDoDia:
    """Reconstrói o estado de um dia: o estoque antigo é um piso, porque pedidos de destino
    desconhecido ficam de fora (docs/dados.md)."""

    war_room: WarRoomRepository
    prioridade: PrioridadeRepository

    def executar(self, dia: date, inicio_da_serie: date | None = None) -> QuadroDoDia:
        calendario = self.war_room.calendario()
        if not calendario.primeiro_dia <= dia <= calendario.hoje:
            raise DiaForaDaJanela
        abertos = self.war_room.abertos_156(dia)
        indicadores = self.prioridade.indicadores_dos_bairros()
        pesos = calcular_pesos(JULGAMENTOS_PADRAO)
        fila = classificar_ocorrencias(abertos, indicadores, pesos)
        fim_da_janela = min(dia, calendario.ultimo_dia)
        return QuadroDoDia(
            dia=dia,
            entradas=self.war_room.entradas_do_dia(dia),
            estoque=self._estoque(dia, abertos, fila, fim_da_janela),
            atraso_por_bairro=_atraso_por_bairro(abertos),
            fila=[_item_da_fila(item) for item in fila[:PEDIDOS_NA_FILA_DO_DIA]],
            serie=self._serie(dia, fim_da_janela, inicio_da_serie),
            categorias=_categorias_com_atraso(abertos),
            categorias_do_dia=self.war_room.mais_entradas(dia, "categoria"),
            bairros_do_dia=self.war_room.mais_entradas(dia, "bairro_oficial"),
        )

    def _serie(
        self, dia: date, fim_da_janela: date, inicio_da_serie: date | None
    ) -> list[DiaDaSerie]:
        if inicio_da_serie is None:
            inicio = fim_da_janela - timedelta(days=DIAS_DA_JANELA - 1)
            return self.war_room.serie(inicio, fim_da_janela)
        fim = inicio_da_serie + timedelta(days=DIAS_SIMULADOS - 1)
        return [
            ponto if ponto.data <= dia else DiaDaSerie(ponto.data, 0, 0)
            for ponto in self.war_room.serie(inicio_da_serie, fim)
        ]

    def _estoque(
        self,
        dia: date,
        abertos: list[Ocorrencia],
        fila: list[OcorrenciaClassificada],
        fim_da_janela: date,
    ) -> EstoqueDoDia:
        janela = timedelta(days=DIAS_DA_JANELA)
        ultimos = self.war_room.serie(fim_da_janela - janela + timedelta(days=1), fim_da_janela)
        anteriores = self.war_room.serie(
            fim_da_janela - 2 * janela + timedelta(days=1), fim_da_janela - janela
        )
        return EstoqueDoDia(
            abertos=len(abertos),
            atrasados=sum(_esta_atrasado(item) for item in abertos),
            classificaveis=len(fila),
            prioritarios=sum(item.indice >= NOTA_ALTA for item in fila),
            com_nota_muito_alta=sum(item.indice >= NOTA_MUITO_ALTA for item in fila),
            camara=self.war_room.sem_resposta_da_camara(dia),
            ouvidoria=self.war_room.alem_do_prazo_da_ouvidoria(dia),
            entradas_nos_ultimos_30=sum(ponto.entradas for ponto in ultimos),
            entradas_nos_30_anteriores=sum(ponto.entradas for ponto in anteriores),
            fim_da_janela=fim_da_janela,
        )
