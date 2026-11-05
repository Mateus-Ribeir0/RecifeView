from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class MotivoDeDescarte(StrEnum):
    LINHA_QUEBRADA = "linha_quebrada"
    SEM_DATA_DE_ABERTURA = "sem_data_de_abertura"
    DATA_INVALIDA = "data_invalida"
    DADO_PESSOAL = "dado_pessoal"
    VALOR_RECUSADO = "valor_recusado"
    REPETIDA_NO_ARQUIVO = "repetida_no_arquivo"


class Correcao(StrEnum):
    PRAZO_NEGATIVO = "prazo_negativo"
    CATEGORIA_UNIFICADA = "categoria_unificada"
    ORGAO_HARMONIZADO = "orgao_harmonizado"
    BAIRRO_RECUPERADO = "bairro_recuperado"
    RPA_PREENCHIDA = "rpa_preenchida"
    BAIRRO_ASSOCIADO = "bairro_associado"
    FECHADO_NO_DIA = "fechado_no_dia"


@dataclass
class RelatorioDeLinhas:
    lidas: int = 0
    aceitas: int = 0
    descartes: Counter[MotivoDeDescarte] = field(default_factory=Counter)
    correcoes: Counter[Correcao] = field(default_factory=Counter)
    datas_invalidas: Counter[str] = field(default_factory=Counter)
    bairros_desconhecidos: Counter[str] = field(default_factory=Counter)
    valores_novos: dict[str, Counter[str]] = field(default_factory=dict)
    repetidas_no_arquivo: int = 0
    sem_id_local: int = 0
    primeira_data: date | None = None
    ultima_data: date | None = None
    fontes: Counter[str] = field(default_factory=Counter)

    def registrar_data(self, data: date) -> None:
        if self.primeira_data is None or data < self.primeira_data:
            self.primeira_data = data
        if self.ultima_data is None or data > self.ultima_data:
            self.ultima_data = data
