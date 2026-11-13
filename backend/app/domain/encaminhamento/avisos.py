from dataclasses import dataclass

from app.domain.encaminhamento.encaminhamento import Encaminhamento, SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import nome_do_orgao
from app.domain.fontes import Fonte

CAMINHO_DO_DETALHE_NA_GESTAO = "/painel/encaminhamentos/"
CAMINHO_DOS_PEDIDOS = "/cidade/meus-pedidos"
CAMINHO_DOS_RELATOS = "/cidade/meus-relatos"
SITUACOES_QUE_AVISAM_O_CIDADAO = frozenset(
    {
        SituacaoDoEncaminhamento.ENVIADO,
        SituacaoDoEncaminhamento.RECEBIDO,
        SituacaoDoEncaminhamento.RESOLVIDO,
        SituacaoDoEncaminhamento.DEVOLVIDO,
    }
)
RESPOSTAS_DO_ORGAO = {
    SituacaoDoEncaminhamento.RECEBIDO: "recebeu e vai tratar",
    SituacaoDoEncaminhamento.RESOLVIDO: "informou que resolveu",
    SituacaoDoEncaminhamento.DEVOLVIDO: "devolveu: informou que a ocorrência não é com ele",
}


@dataclass(frozen=True)
class Aviso:
    assunto: str
    corpo: str


def _data(encaminhamento: Encaminhamento) -> str:
    return encaminhamento.prazo_de_resposta.strftime("%d/%m/%Y")


def _o_que_aconteceu(encaminhamento: Encaminhamento) -> str:
    orgao = nome_do_orgao(encaminhamento.orgao)
    if encaminhamento.situacao is SituacaoDoEncaminhamento.ENVIADO:
        return f"foi encaminhado para {orgao}, que tem até {_data(encaminhamento)} para resolver"
    if encaminhamento.situacao is SituacaoDoEncaminhamento.RECEBIDO:
        return f"foi recebido por {orgao}"
    if encaminhamento.situacao is SituacaoDoEncaminhamento.RESOLVIDO:
        return f"foi resolvido, segundo {orgao}"
    return (
        f"foi devolvido por {orgao}, que informou não ser o responsável."
        " A gestão vai escolher outro destino"
    )


def aviso_a_gestao(encaminhamento: Encaminhamento, endereco_do_site: str) -> Aviso:
    orgao = nome_do_orgao(encaminhamento.orgao)
    resposta = RESPOSTAS_DO_ORGAO.get(encaminhamento.situacao, encaminhamento.situacao.value)
    linhas = [f"{orgao} {resposta} ({encaminhamento.codigo})."]
    if encaminhamento.protocolo_do_orgao:
        linhas.append(f"Protocolo no órgão: {encaminhamento.protocolo_do_orgao}.")
    if encaminhamento.ultima_observacao:
        linhas.append(f"Observação do órgão: {encaminhamento.ultima_observacao}")
    if encaminhamento.situacao is SituacaoDoEncaminhamento.DEVOLVIDO:
        linhas.append("A ocorrência pode seguir para outro órgão pelo detalhe do encaminhamento.")
    detalhe = f"{endereco_do_site.rstrip('/')}{CAMINHO_DO_DETALHE_NA_GESTAO}{encaminhamento.id}"
    linhas += ["", detalhe]
    return Aviso(f"{orgao} respondeu {encaminhamento.codigo}", "\n".join(linhas))


def aviso_ao_cidadao(encaminhamento: Encaminhamento, endereco_do_site: str) -> Aviso:
    """Só a etapa e o órgão: sem endereço, sem texto e sem a justificativa da gestão."""
    ocorrencia = encaminhamento.ocorrencia
    veio_do_formulario = ocorrencia.fonte == Fonte.FORMULARIO.value
    if veio_do_formulario:
        assunto_do_pedido = "O problema que você relatou"
        caminho = CAMINHO_DOS_RELATOS
    else:
        assunto_do_pedido = f"O seu pedido de protocolo {ocorrencia.protocolo}"
        caminho = CAMINHO_DOS_PEDIDOS
    corpo = "\n".join(
        [
            f"{assunto_do_pedido} {_o_que_aconteceu(encaminhamento)}.",
            "",
            "Acompanhe as etapas na sua área:",
            f"{endereco_do_site.rstrip('/')}{caminho}",
            "",
            "Para não receber estes avisos, desligue em Minha conta.",
        ]
    )
    return Aviso(f"Andamento: {nome_do_orgao(encaminhamento.orgao)}", corpo)
