from dataclasses import dataclass
from datetime import date

from app.domain.encaminhamento.encaminhamento import Encaminhamento, SituacaoDoEncaminhamento
from app.domain.encaminhamento.orgaos import nome_do_orgao
from app.domain.fontes import Fonte

CAMINHO_DO_DETALHE_NA_GESTAO = "/painel/encaminhamentos/"
CAMINHO_DO_DETALHE_NO_ORGAO = "/corporativo/ocorrencias/"
CAMINHO_DOS_PEDIDOS = "/cidade/meus-pedidos"
CAMINHO_DOS_RELATOS = "/cidade/meus-relatos"
SEM_TEMA = "ocorrência sem tema"
SEM_BAIRRO = "bairro não informado"
SITUACOES_QUE_AVISAM_O_CIDADAO = frozenset(
    {
        SituacaoDoEncaminhamento.ENVIADO,
        SituacaoDoEncaminhamento.RECEBIDO,
        SituacaoDoEncaminhamento.RESOLVIDO,
        SituacaoDoEncaminhamento.DEVOLVIDO,
    }
)
RESPOSTAS_DO_ORGAO = {
    SituacaoDoEncaminhamento.RECEBIDO: "está atendendo",
    SituacaoDoEncaminhamento.RESOLVIDO: "informou que resolveu",
    SituacaoDoEncaminhamento.DEVOLVIDO: "devolveu: informou que a ocorrência não é com ele",
}


@dataclass(frozen=True)
class Aviso:
    """O e-mail usa assunto e corpo; o sino da plataforma usa assunto, resumo e caminho."""

    assunto: str
    corpo: str
    resumo: str
    caminho: str


def _data(valor: date) -> str:
    return valor.strftime("%d/%m/%Y")


def _endereco(endereco_do_site: str, caminho: str) -> str:
    return f"{endereco_do_site.rstrip('/')}{caminho}"


def _tema_e_bairro(encaminhamento: Encaminhamento) -> str:
    ocorrencia = encaminhamento.ocorrencia
    tema = (ocorrencia.categoria or SEM_TEMA).capitalize()
    return f"{tema} em {ocorrencia.bairro_oficial or SEM_BAIRRO}"


def _o_que_aconteceu(encaminhamento: Encaminhamento) -> str:
    orgao = nome_do_orgao(encaminhamento.orgao)
    situacao = encaminhamento.situacao
    if situacao is SituacaoDoEncaminhamento.ENVIADO:
        prazo = _data(encaminhamento.prazo_de_resposta)
        return f"foi encaminhado para {orgao}, que tem até {prazo} para resolver"
    if situacao is SituacaoDoEncaminhamento.RECEBIDO:
        return f"está em atendimento por {orgao}"
    if situacao is SituacaoDoEncaminhamento.RESOLVIDO:
        return f"foi resolvido, segundo {orgao}"
    return (
        f"foi devolvido por {orgao}, que informou não ser o responsável."
        " A gestão vai escolher outro destino"
    )


def _linhas_da_resposta(encaminhamento: Encaminhamento) -> list[str]:
    linhas: list[str] = []
    if encaminhamento.resposta_ao_cidadao:
        orgao = nome_do_orgao(encaminhamento.orgao)
        linhas.append(f"Resposta de {orgao}: {encaminhamento.resposta_ao_cidadao}")
    if encaminhamento.previsao:
        linhas.append(f"Previsão de conclusão: {_data(encaminhamento.previsao)}.")
    return linhas


def aviso_a_gestao(encaminhamento: Encaminhamento, endereco_do_site: str) -> Aviso:
    orgao = nome_do_orgao(encaminhamento.orgao)
    resposta = RESPOSTAS_DO_ORGAO.get(encaminhamento.situacao, encaminhamento.situacao.value)
    resumo = f"{orgao} {resposta} ({encaminhamento.codigo})."
    linhas = [resumo]
    if encaminhamento.protocolo_do_orgao:
        linhas.append(f"Protocolo no órgão: {encaminhamento.protocolo_do_orgao}.")
    if encaminhamento.ultima_observacao:
        linhas.append(f"Observação do órgão: {encaminhamento.ultima_observacao}")
    linhas += _linhas_da_resposta(encaminhamento)
    if encaminhamento.situacao is SituacaoDoEncaminhamento.DEVOLVIDO:
        linhas.append("A ocorrência pode seguir para outro órgão pelo detalhe do encaminhamento.")
    caminho = f"{CAMINHO_DO_DETALHE_NA_GESTAO}{encaminhamento.id}"
    linhas += ["", _endereco(endereco_do_site, caminho)]
    assunto = f"{orgao} respondeu {encaminhamento.codigo}"
    return Aviso(assunto, "\n".join(linhas), resumo, caminho)


def aviso_ao_cidadao(encaminhamento: Encaminhamento, endereco_do_site: str) -> Aviso:
    """Etapa, órgão e a resposta ao cidadão. Nunca a nota interna nem a justificativa da gestão."""
    ocorrencia = encaminhamento.ocorrencia
    if ocorrencia.fonte == Fonte.FORMULARIO.value:
        assunto_do_pedido = "O problema que você relatou"
        caminho = CAMINHO_DOS_RELATOS
    else:
        assunto_do_pedido = f"O seu pedido de protocolo {ocorrencia.protocolo}"
        caminho = CAMINHO_DOS_PEDIDOS
    resumo = f"{assunto_do_pedido} {_o_que_aconteceu(encaminhamento)}."
    corpo = "\n".join(
        [
            resumo,
            *_linhas_da_resposta(encaminhamento),
            "",
            "Acompanhe as etapas na sua área:",
            _endereco(endereco_do_site, caminho),
            "",
            "Para não receber estes avisos por e-mail, desligue em Minha conta.",
        ]
    )
    return Aviso(f"Andamento: {nome_do_orgao(encaminhamento.orgao)}", corpo, resumo, caminho)


def aviso_de_nova_ocorrencia(encaminhamento: Encaminhamento, endereco_do_site: str) -> Aviso:
    prazo = _data(encaminhamento.prazo_de_resposta)
    orgao = nome_do_orgao(encaminhamento.orgao)
    resumo = f"{encaminhamento.codigo}: {_tema_e_bairro(encaminhamento)}. Prazo até {prazo}."
    caminho = f"{CAMINHO_DO_DETALHE_NO_ORGAO}{encaminhamento.id}"
    corpo = "\n".join(
        [
            f"A gestão da Prefeitura encaminhou uma ocorrência a {orgao}.",
            "",
            resumo,
            "",
            "Veja onde fica e responda na área corporativa:",
            _endereco(endereco_do_site, caminho),
        ]
    )
    return Aviso(f"Nova ocorrência {encaminhamento.codigo}", corpo, resumo, caminho)


def aviso_de_prazo_vencido(encaminhamento: Encaminhamento, endereco_do_site: str) -> Aviso:
    prazo = _data(encaminhamento.prazo_de_resposta)
    resumo = (
        f"O prazo de {encaminhamento.codigo} ({_tema_e_bairro(encaminhamento)}) venceu em"
        f" {prazo} sem resposta final."
    )
    caminho = f"{CAMINHO_DO_DETALHE_NO_ORGAO}{encaminhamento.id}"
    corpo = "\n".join(
        [
            resumo,
            "",
            "Informe o andamento, resolva ou devolva à gestão na área corporativa:",
            _endereco(endereco_do_site, caminho),
        ]
    )
    return Aviso(f"Prazo vencido: {encaminhamento.codigo}", corpo, resumo, caminho)
