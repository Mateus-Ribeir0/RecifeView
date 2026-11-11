from datetime import date, datetime

from pydantic import BaseModel, Field

from app.api.schemas.painel import Esquema
from app.application.casos_de_uso.pedidos.meus_pedidos import PedidoComAndamento
from app.domain.encaminhamento.encaminhamento import Encaminhamento, SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import Orgao, nome_do_orgao
from app.domain.fontes import ROTULOS_DAS_FONTES
from app.domain.pedido import AndamentoDoPedido
from app.domain.protocolo import TAMANHO_MAXIMO_DO_PROTOCOLO

ROTULOS_POR_FONTE = {fonte.value: rotulo for fonte, rotulo in ROTULOS_DAS_FONTES.items()}
FOLGA_PARA_ESPACOS = 20


class ProtocoloEntrada(BaseModel):
    protocolo: str = Field(max_length=TAMANHO_MAXIMO_DO_PROTOCOLO + FOLGA_PARA_ESPACOS)


class EtapaPublicaResposta(Esquema):
    situacao: SituacaoDoEncaminhamento
    ocorrido_em: datetime


class EncaminhamentoPublicoResposta(BaseModel):
    """Sem justificativa nem observação: o texto é da gestão e do órgão, não da pessoa."""

    codigo: str
    orgao: Orgao
    nome_do_orgao: str
    situacao: SituacaoDoEncaminhamento
    atrasado: bool
    encaminhado_em: datetime
    prazo_de_resposta: date
    protocolo_do_orgao: str | None
    etapas: list[EtapaPublicaResposta]

    @classmethod
    def de_encaminhamento(cls, item: Encaminhamento, hoje: date) -> "EncaminhamentoPublicoResposta":
        return cls(
            codigo=item.codigo,
            orgao=item.orgao,
            nome_do_orgao=nome_do_orgao(item.orgao),
            situacao=item.situacao,
            atrasado=item.esta_atrasado(hoje),
            encaminhado_em=item.criado_em,
            prazo_de_resposta=item.prazo_de_resposta,
            protocolo_do_orgao=item.protocolo_do_orgao,
            etapas=[EtapaPublicaResposta.model_validate(evento) for evento in item.eventos],
        )


class AndamentoResposta(BaseModel):
    fonte: str
    rotulo_da_fonte: str
    protocolo: str
    data_abertura: date | None
    categoria: str | None
    servico: str | None
    tipo_registro: str | None
    orgao: str | None
    situacao: str | None
    data_ult_movimento: date | None
    prazo_da_fonte: date | None
    bairro_oficial: str | None
    rpa: str | None
    encaminhamentos: list[EncaminhamentoPublicoResposta]

    @classmethod
    def de_andamento(cls, andamento: AndamentoDoPedido, hoje: date) -> "AndamentoResposta":
        registro = andamento.registro
        return cls(
            fonte=registro.fonte,
            rotulo_da_fonte=ROTULOS_POR_FONTE.get(registro.fonte, registro.fonte),
            protocolo=registro.protocolo,
            data_abertura=registro.data_abertura,
            categoria=registro.categoria,
            servico=registro.servico,
            tipo_registro=registro.tipo_registro,
            orgao=registro.orgao,
            situacao=registro.situacao,
            data_ult_movimento=registro.data_ult_movimento,
            prazo_da_fonte=registro.prazo_da_fonte,
            bairro_oficial=registro.bairro_oficial,
            rpa=registro.rpa,
            encaminhamentos=[
                EncaminhamentoPublicoResposta.de_encaminhamento(item, hoje)
                for item in andamento.encaminhamentos
            ],
        )


class PedidoAcompanhadoResposta(BaseModel):
    id: int
    protocolo: str
    criado_em: datetime
    andamentos: list[AndamentoResposta]

    @classmethod
    def de_pedido(cls, item: PedidoComAndamento, hoje: date) -> "PedidoAcompanhadoResposta":
        return cls(
            id=item.pedido.id,
            protocolo=item.pedido.protocolo,
            criado_em=item.pedido.criado_em,
            andamentos=[
                AndamentoResposta.de_andamento(andamento, hoje) for andamento in item.andamentos
            ],
        )
