from datetime import datetime

from pydantic import BaseModel

from app.domain.notificacao import CaixaDeNotificacoes, Notificacao


class NotificacaoResposta(BaseModel):
    id: int
    titulo: str
    texto: str
    caminho: str
    criada_em: datetime
    lida: bool

    @classmethod
    def de_notificacao(cls, notificacao: Notificacao) -> "NotificacaoResposta":
        return cls(
            id=notificacao.id,
            titulo=notificacao.titulo,
            texto=notificacao.texto,
            caminho=notificacao.caminho,
            criada_em=notificacao.criada_em,
            lida=notificacao.foi_lida,
        )


class CaixaDeNotificacoesResposta(BaseModel):
    nao_lidas: int
    itens: list[NotificacaoResposta]

    @classmethod
    def de_caixa(cls, caixa: CaixaDeNotificacoes) -> "CaixaDeNotificacoesResposta":
        return cls(
            nao_lidas=caixa.nao_lidas,
            itens=[NotificacaoResposta.de_notificacao(item) for item in caixa.itens],
        )
