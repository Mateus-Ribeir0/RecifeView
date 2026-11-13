from dataclasses import dataclass
from datetime import date

from app.domain.encaminhamento.encaminhamento import Encaminhamento
from app.domain.encaminhamento.orgaos import Orgao, nome_do_orgao
from app.domain.fontes import ROTULOS_DAS_FONTES

NAO_INFORMADO = "não informado"
SEM_PROTOCOLO = "a fonte não publica protocolo"
ROTULOS_POR_FONTE = {fonte.value: rotulo for fonte, rotulo in ROTULOS_DAS_FONTES.items()}


@dataclass(frozen=True)
class MensagemAoOrgao:
    orgao: Orgao
    codigo: str
    assunto: str
    corpo: str
    dados: dict[str, object]


def _data(valor: date | None) -> str:
    return valor.strftime("%d/%m/%Y") if valor else NAO_INFORMADO


def _nota(valor: float | None) -> str:
    return f"{valor:.1f} de 10".replace(".", ",") if valor is not None else NAO_INFORMADO


def _dados(encaminhamento: Encaminhamento, link_de_retorno: str) -> dict[str, object]:
    ocorrencia = encaminhamento.ocorrencia
    return {
        "codigo": encaminhamento.codigo,
        "orgao": encaminhamento.orgao.value,
        "fonte": ocorrencia.fonte,
        "protocolo_de_origem": ocorrencia.protocolo,
        "data_abertura": ocorrencia.data_abertura.isoformat() if ocorrencia.data_abertura else None,
        "categoria": ocorrencia.categoria,
        "servico": ocorrencia.servico,
        "bairro_oficial": ocorrencia.bairro_oficial,
        "rpa": ocorrencia.rpa,
        "local_aproximado": ocorrencia.referencia_de_local,
        "situacao_na_fonte": ocorrencia.situacao,
        "nota": encaminhamento.nota,
        "justificativa": encaminhamento.justificativa,
        "prazo_de_resposta": encaminhamento.prazo_de_resposta.isoformat(),
        "link_de_retorno": link_de_retorno,
    }


def _linhas_da_ocorrencia(encaminhamento: Encaminhamento) -> list[str]:
    ocorrencia = encaminhamento.ocorrencia
    bairro = ocorrencia.bairro_oficial or NAO_INFORMADO
    rpa = f" (RPA {ocorrencia.rpa})" if ocorrencia.rpa else ""
    return [
        f"Código: {encaminhamento.codigo}",
        f"Fonte: {ROTULOS_POR_FONTE.get(ocorrencia.fonte, ocorrencia.fonte)}",
        f"Protocolo de origem: {ocorrencia.protocolo or SEM_PROTOCOLO}",
        f"Aberta em: {_data(ocorrencia.data_abertura)}",
        f"Tema: {ocorrencia.categoria or NAO_INFORMADO}",
        f"Serviço: {ocorrencia.servico or NAO_INFORMADO}",
        f"Bairro: {bairro}{rpa}",
        *(
            [f"Local aproximado: {ocorrencia.referencia_de_local}"]
            if ocorrencia.referencia_de_local
            else []
        ),
        f"Situação na fonte: {ocorrencia.situacao or NAO_INFORMADO}",
        f"Nota de prioridade: {_nota(encaminhamento.nota)}",
        f"Justificativa da gestão: {encaminhamento.justificativa or NAO_INFORMADO}",
    ]


def montar_mensagem(
    encaminhamento: Encaminhamento, link_de_retorno: str, link_vale_ate: date
) -> MensagemAoOrgao:
    prazo = _data(encaminhamento.prazo_de_resposta)
    corpo = "\n".join(
        [
            f"A gestão encaminhou ao órgão {nome_do_orgao(encaminhamento.orgao)} uma ocorrência"
            " priorizada no RecifeView.",
            "",
            *_linhas_da_ocorrencia(encaminhamento),
            "",
            f"Prazo para resolver ou devolver: {prazo} (Lei 13.460/2017, art. 16).",
            "",
            "Para informar que recebeu, que resolveu ou que a ocorrência não é com o seu órgão,"
            " use o link abaixo. Ele vale só para este encaminhamento,"
            f" até {_data(link_vale_ate)}.",
            link_de_retorno,
        ]
    )
    return MensagemAoOrgao(
        orgao=encaminhamento.orgao,
        codigo=encaminhamento.codigo,
        assunto=f"Ocorrência encaminhada {encaminhamento.codigo}",
        corpo=corpo,
        dados=_dados(encaminhamento, link_de_retorno),
    )


def montar_lembrete(
    encaminhamento: Encaminhamento, link_de_retorno: str, link_vale_ate: date
) -> MensagemAoOrgao:
    """Sai quando o prazo vence sem resposta final. O link novo substitui o da primeira mensagem."""
    original = montar_mensagem(encaminhamento, link_de_retorno, link_vale_ate)
    abertura = (
        f"Lembrete: o prazo de {_data(encaminhamento.prazo_de_resposta)} para resolver ou devolver"
        f" a ocorrência {encaminhamento.codigo} venceu e ainda não há resposta final do órgão."
        " Este link substitui o da mensagem anterior."
    )
    return MensagemAoOrgao(
        orgao=original.orgao,
        codigo=original.codigo,
        assunto=f"Lembrete: prazo vencido da ocorrência {encaminhamento.codigo}",
        corpo=f"{abertura}\n\n{original.corpo}",
        dados={**original.dados, "lembrete": True},
    )
