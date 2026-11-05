from datetime import date
from typing import NamedTuple


class RegistroDeDemanda(NamedTuple):
    chave_registro: int
    assinatura: int
    fonte: str
    ano: int | None
    data_abertura: date | None
    data_ult_movimento: date | None
    dias_ate_movimento: int | None
    prazo_negativo: bool
    categoria: str | None
    servico_codigo: str | None
    servico: str | None
    tipo_registro: str | None
    orgao: str | None
    canal_entrada: str | None
    bairro_oficial: str | None
    bairro_recuperado: bool
    rpa: str | None
    situacao: str | None
    iniciativa: str | None
    id_local: str | None
    numero_informado: bool | None
    ouv_data_prazo: date | None
    ouv_no_prazo: bool | None
    camara_data_envio_prefeitura: date | None
    camara_canal_envio: str | None
    camara_dias_ate_envio: int | None
    camara_data_resposta: date | None
    camara_dias_ate_resposta: int | None
    camara_desfecho: str | None
    arquivo_origem: str | None
    ano_do_arquivo: int | None
